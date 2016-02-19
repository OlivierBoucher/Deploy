from paramiko import SSHClient, AutoAddPolicy


class Server(object):
    """"""

    def __init__(self, address, user):
        self.address = address
        self.user = user

    def has_valid_connection(self):
        client = SSHClient()
        try:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(self.address, username=self.user)
        except IOError, e:
            return False, e
        finally:
            client.close()

        return True, None
