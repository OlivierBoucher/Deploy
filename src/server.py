import errno

from paramiko import SSHClient, SFTPClient, AutoAddPolicy

from utilities import get_bash_script, get_string

from terminal import Terminal


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

        return ret_code is '0'

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
                    if self.user is not 'root' and self.password is None:
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
        stdout, stderr = self._execute_sudo_cmd('sudo %s install -y %s' % (pm, dep))

        ret, error = stdout.read().rstrip(), stderr.read().rstrip()
        if error is not '':
            self.password = None

        return error is ''

    def _execute_sudo_cmd(self, cmd):
        transport = self.ssh_client.get_transport()
        session = transport.open_session()
        session.get_pty()

        session.exec_command(cmd)
        stdin = session.makefile('wb', -1)
        stdout = session.makefile('rb', -1)
        stderr = session.makefile_stderr('rb', -1)

        stdin.write('%s\n' % self.password)
        stdin.flush()

        return stdout, stderr

    def _prompt_superuser_pwd(self, label):
        """"""
        self.password = get_string(label, password=True)
        return self.password

    def _has_directory(self, sftp, directory):
        try:
            sftp.stat(directory)
        except IOError, e:
            if e.errno is errno.ENOENT:
                return False
            else:
                raise
        return True

    def _create_directory(self, directory):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command('mkdir -p %s' % directory)
            out, err = stdout.read().rstrip(), stderr.read().rstrip()
            return out is '' and err is ''
        except IOError, e:
            return False

    def has_directories(self, directories, auto_create=True):
        try:
            self.ssh_client.connect(self.address, username=self.user)
            sftp_client = SFTPClient.from_transport(self.ssh_client.get_transport())

            for directory in directories:
                if not self._has_directory(sftp_client, directory) and auto_create:
                    Terminal.print_warn('Missing directory "%s", attempting to create.' % directory)
                    if not self._create_directory(directory):
                        raise ServerError('Could not create directory "%s"' % directory)
                else:
                    raise ServerError('Missing directory "%s"' % directory)

        except IOError, e:
                raise ServerError('An error occurred with the ssh connection.\n\t> %s' % e, base=e)
        finally:
            self.ssh_client.close()
