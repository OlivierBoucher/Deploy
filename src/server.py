from paramiko import SSHClient, AutoAddPolicy

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

            return stdout.read().rstrip()

        except IOError, e:
            return False, e
        finally:
            self.client.close()
