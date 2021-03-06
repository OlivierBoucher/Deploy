from paramiko import SSHClient, AutoAddPolicy

from utilities import get_bash_script, get_string

from terminal import Terminal

from socket import timeout


class ServerError(Exception):
    """ Base error class for Server """

    def __init__(self, message, base=None):
        super(ServerError, self).__init__(message)
        self.base_exception = base


class Server(object):
    """ Represents a target remote server """
    SCRIPT_DEP_INSTALLED = 'dependencies_installed'
    SCRIPT_DETECT_PM = 'detect_pm'

    def __init__(self, address, user):
        self.address = address
        self.user = user
        self.password = None
        self.ssh_client = SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())

    def has_valid_connection(self):
        """ Validates the SSH connection to a remote server.

        Returns:
            bool: If the connection is valid.

        """
        try:
            self.ssh_client.connect(self.address, username=self.user)
        except IOError, e:
            return False, e
        finally:
            self.ssh_client.close()

        return True, None

    def _get_package_manager(self):
        """ Gets the remote server package manager in an OS agnostic way.

        Returns:
            string: The package manager, if supported.

        Raises:
            ServerError: If the connection closes or we fail to retrieve the package manager.

        """
        stdin, stdout, stderr = self.ssh_client.exec_command(
            "bash -c '%s'" % get_bash_script(Server.SCRIPT_DETECT_PM))

        package_manager = stdout.read().rstrip()

        if package_manager.startswith('[ERROR]'):
            raise ServerError('Could not retrieve the package manager.\n\t> %s' % package_manager)

        return package_manager

    def _validate_single_dep_installed(self, pm, dep):
        """ Validates that a specific dependency is installed on the remote server.

        Args:
            pm (string): The server's package manager name.
            dep (string: The dependency to validate.

        Returns:
            bool: If the dependency is installed.

        """
        script = "%s\nis_installed %s %s" % (get_bash_script(Server.SCRIPT_DEP_INSTALLED), pm, dep)
        command = "bash -c '%s'" % script
        stdin, stdout, stderr = self.ssh_client.exec_command(command)

        ret_code, errors = stdout.read().rstrip(), stderr.read().rstrip()

        # if errors is not '':
        # Terminal.print_warn('Got errors from dependency checker script.\n\t> %s' % errors)

        return ret_code == '0'

    def validate_dep_list_installed(self, deps):
        """ Validates that certain dependencies are installed on the remote server.

        Args:
            deps (list): The list of dependencies to validate against (Strings).

        Raises:
            ServerError: If a dependency is missing.

        """
        try:
            self.ssh_client.connect(self.address, username=self.user)
            pm = self._get_package_manager()
            for dep in deps:
                if not self._validate_single_dep_installed(pm, dep):
                    if self.user != 'root' and self.password is None:
                        self._prompt_superuser_pwd(
                            'Missing dependency "%s". Please enter password to proceed to installation.' % dep)

                    if not self._install_dependency(pm, dep):
                        raise ServerError('Could not install dependency "%s".' % dep)
                    else:
                        print 'Successfully installed "%s".' % dep
        except IOError, e:
            raise ServerError('An error occurred with the ssh connection.\n\t> %s' % e, base=e)
        finally:
            self.ssh_client.close()

    def _install_dependency(self, pm, dep):
        ret, error = self._execute_sudo_cmd('%s install -y %s' % (pm, dep))

        if error != '':
            self.password = None

        return error == ''

    def _execute_sudo_cmd(self, cmd):
        transport = self.ssh_client.get_transport()
        session = transport.open_session()
        session.settimeout(3)
        session.get_pty()

        try:
            session.exec_command("sudo -k %s" % cmd)
            stdin = session.makefile('wb', -1)
            stdout = session.makefile('rb', -1)
            stderr = session.makefile_stderr('rb', -1)

            stdin.write('%s\n' % self.password)
            stdin.flush()

            return stdout.read().rstrip(), stderr.read().rstrip()

        except timeout, e:
            return "", "Invalid password."

    def _prompt_superuser_pwd(self, label):
        """"""
        self.password = get_string(label, password=True)
        return self.password

    def _has_file(self, file):
        stdin, stdout, stderr = self.ssh_client.exec_command('stat %s' % file)

        out, err = stdout.read().rstrip(), stderr.read().rstrip()

        return not err.endswith('No such file or directory')

    def _create_directory(self, directory):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command('mkdir -p %s' % directory)
            out, err = stdout.read().rstrip(), stderr.read().rstrip()
            return out == '' and err == ''
        except IOError, e:
            return False

    def has_directories(self, directories, auto_create=True):
        try:
            self.ssh_client.connect(self.address, username=self.user)

            for directory in directories:
                if not self._has_file(directory):
                    if auto_create:
                        Terminal.print_warn('Missing directory "%s", attempting to create.' % directory)
                        if not self._create_directory(directory):
                            raise ServerError('Could not create directory "%s"' % directory)
                    else:
                        raise ServerError('Missing directory "%s".' % directory)

        except IOError, e:
            raise ServerError('An error occurred with the ssh connection.\n\t> %s' % e, base=e)
        finally:
            self.ssh_client.close()

    def _init_repo(self, path, bare=False):
        cmd = 'cd %s && git init' % path
        if bare:
            cmd = '%s --bare' % cmd
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd)

        out, err = stdout.read().rstrip(), stderr.read().rstrip()

        return out.startswith('Initialized empty Git repository') and err == ''

    def _clone_repo(self, bare_repo_directory, src_repo_directory):
        stdin, stdout, stderr = self.ssh_client.exec_command(
            'git clone %s %s' % (bare_repo_directory, src_repo_directory))

        out, err = stdout.read().rstrip(), stderr.read().rstrip()

        return out.endswith('done.') or err.endswith('done.')

    def _is_repo(self, path, bare=False):

        if bare:
            for item in ['branches', 'config', 'description', 'HEAD', 'hooks', 'info', 'objects', 'refs']:
                if not self._has_file('%s/%s' % (path, item)):
                    return False
            return True
        else:
            return self._has_file('%s/.git' % path)

    def has_git_repositories(self, bare_repo_directory, src_repo_directory, auto_create=True):
        try:
            self.ssh_client.connect(self.address, username=self.user)

            if not self._is_repo(bare_repo_directory, bare=True):
                if auto_create:
                    Terminal.print_warn('No bare git repository in "%s", attempting to create.' % bare_repo_directory)
                    if not self._init_repo(bare_repo_directory, bare=True):
                        raise ServerError('Could not create bare git repository in "%s"' % bare_repo_directory)
                else:
                    raise ServerError('Missing bare git repository in "%s".' % bare_repo_directory)

            if not self._is_repo(src_repo_directory, bare=False):
                if auto_create:
                    Terminal.print_warn('No src git repository in "%s", attempting to create.' % src_repo_directory)
                    if not self._clone_repo(bare_repo_directory, src_repo_directory):
                        raise ServerError('Could not create src git repository in "%s"' % src_repo_directory)
                else:
                    raise ServerError('Missing src git repository in "%s".' % src_repo_directory)
        except IOError, e:
            raise ServerError('An error occurred with the ssh connection.\n\t> %s' % e, base=e)
        finally:
            self.ssh_client.close()

    def _is_service_running(self, service):
        stdin, stdout, stderr = self.ssh_client.exec_command(
            "bash -c 'ps -ef | grep -v grep | grep -q %s; echo $?'" % service)

        ret_code, errors = stdout.read().rstrip(), stderr.read().rstrip()

        return ret_code == '0'

    def get_supervisor_config(self, project, auto_create=True):
        try:
            self.ssh_client.connect(self.address, username=self.user)

            ubuntu_config_dir = '/etc/supervisor/conf.d'
            rehl_config_dir = '/etc/supervisord.d'
            config_path = ''

            if self._has_file(ubuntu_config_dir):
                config_path = "%s/%s.conf" % (ubuntu_config_dir, project.lower())
            elif self._has_file(rehl_config_dir):
                config_path = '%s/%s.conf' % (rehl_config_dir, project.lower())
            else:
                raise ServerError('Could not find supervisor include dir')

            if not self._has_file(config_path):
                if auto_create:
                    Terminal.print_warn(
                        'Missing supervisor config for %s in "%s", attempting to create.' % (project, config_path))

                    if self.user != 'root' and self.password is None:
                        self._prompt_superuser_pwd(
                            'Missing file "%s", Please enter password to proceed to creation.' % config_path)

                    out, err = self._execute_sudo_cmd('touch %s' % config_path)

                    if err != '':
                        self.password = None
                        raise ServerError('Could not create supervisor config in "%s" : %s' % (config_path, err))

                    return ''
                else:
                    raise ServerError('Missing supervisor config for %s in "%s".' % (project, config_path))

            stdin, stdout, stderr = self.ssh_client.exec_command('cat %s' % config_path)

            out, err = stdout.read().rstrip(), stderr.read().rstrip()

            if err != '':
                raise ServerError('Could not read supervisor config "%s"' % config_path)

            return out
        except IOError, e:
            raise ServerError('An error occurred with the ssh connection.\n\t> %s' % e, base=e)
        finally:
            self.ssh_client.close()

    def set_supervisor_config(self, project, config):
        try:
            self.ssh_client.connect(self.address, username=self.user)

            ubuntu_config_dir = '/etc/supervisor/conf.d'
            rehl_config_dir = '/etc/supervisord.d'
            config_path = ''

            if self._has_file(ubuntu_config_dir):
                config_path = "%s/%s.conf" % (ubuntu_config_dir, project.lower())
            elif self._has_file(rehl_config_dir):
                config_path = '%s/%s.conf' % (rehl_config_dir, project.lower())
            else:
                raise ServerError('Could not find supervisor include dir')

            if self.user != 'root' and self.password is None:
                self._prompt_superuser_pwd(
                    'Need to write configuration to "%s", please enter password to proceed.' % config_path)

            out, err = self._execute_sudo_cmd("bash -c 'echo \"%s\" > %s'" % (config, config_path))

            if err != '':
                raise ServerError('Could not write to config in "%s" : %s' % (config_path, err))

        except IOError, e:
            raise ServerError('An error occurred with the ssh connection.\n\t> %s' % e, base=e)
        finally:
            self.ssh_client.close()
