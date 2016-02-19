from paramiko import SSHClient, AutoAddPolicy

from terminal import Terminal

from utilities import get_bash_script


class ServerError(Exception):
    def __init__(self, message, base=None):
        super(ServerError, self).__init__(message)
        self.base_exception = base


class Server(object):
    """"""
    SCRIPT_DEP_INSTALLED = 'dependencies_installed'
    SCRIPT_DETECT_PM = 'detect_pm'

    def __init__(self, address, user):
        self.address = address
        self.user = user
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

    def has_valid_connection(self):
        try:
            self.client.connect(self.address, username=self.user)
        except IOError, e:
            return False, e
        finally:
            self.client.close()

        return True, None

    def _get_package_manager(self):
        try:
            self.client.connect(self.address, username=self.user)
            stdin, stdout, stderr = self.client.exec_command(
                "bash -c '%s'" % get_bash_script(Server.SCRIPT_DETECT_PM))

            package_manager = stdout.read().rstrip()

            if package_manager.startswith('[ERROR]'):
                raise ServerError('Could not retrieve the package manager.\n\t> %s' % package_manager)

            return package_manager

        except IOError, e:
            raise ServerError('An error occurred with the ssh connection.\n\t> %s' % e, base=e)
        finally:
            self.client.close()

    def _validate_single_dep_installed(self, pm, dep):
        script = "%s\nis_installed %s %s" % (get_bash_script(Server.SCRIPT_DEP_INSTALLED), pm, dep)
        command = "bash -c '%s'" % script
        stdin, stdout, stderr = self.client.exec_command(command)

        ret_code, errors = stdout.read().rstrip(), stderr.read().rstrip()

        if errors is not '':
            Terminal.print_warn('Got errors from dependency checker script.\n\t> %s' % errors)

        return ret_code is '0'

    def validate_dep_list_installed(self, deps):
        try:
            pm = self._get_package_manager()
            self.client.connect(self.address, username=self.user)
            for dep in deps:
                if not self._validate_single_dep_installed(pm, dep):
                    raise ServerError('Missing dependecy "{0}". Please install using "{1} install {0}"'.format(dep, pm))

        except IOError, e:
            raise ServerError('An error occurred with the ssh connection.\n\t> %s' % e, base=e)
        finally:
            self.client.close()
