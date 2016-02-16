import os, json
from utilities import get_string, valid_address, valid_ssh_connection

class Deploy(object):
    def __init__(self, command, config):
        self.cmd = command
        self.config = config
        self.commands = {
            'init': self.__cmd_init,
            'now': self.__cmd_now,
        }
        self.presets = {
            'java:gradle': '',
            'java:maven' : '',
            'js:node': ''
        }

    def __cmd_init(self):
        # Local info
        #   Project name, default to current dir
        dir = os.path.basename(os.getcwd())
        project = get_string(
            'Enter the project\'s name.',
            default=dir,
            validate=lambda x: x is not '',
            error_msg='The project field cannot be empty.\n')
        
        #   Preset, must choose from available presets
        presets_list = reduce(lambda x, y: x + '\n\t- ' + y, self.presets)
        preset = get_string(
            'Select the apropriate preset.',
            validate=lambda x: x in self.presets,
            error_msg='The selected preset does not exist. Please refer to this list:\n\t- ' + presets_list)
        
        #   Source dir
        source_dir = get_string(
            'Enter the source directory relative path. (Optional)',
            validate=lambda x: x is '' or os.path.exists(os.getcwd() + '/' + x),
            error_msg='The selected directory does not exist')
        
        #   Build dir
        build_dir = get_string(
            'Enter the build directory containing the binaries relative path. (Optional)',
            validate=lambda x: x is '' or os.path.exists(os.getcwd() + '/' + x),
            error_msg='The selected directory does not exist')
        
        # Remote
        #   Server address
        srv_address = get_string(
            'Enter the remote server address.',
            validate=valid_address,
            error_msg='The address must be a valid IP or hostname.')
        
        #   Server user
        srv_user = get_string(
            'Enter the remote server user.',
            validate=lambda x: x is not '',
            error_msg='The user field cannot be empty.')
        
        # Test SSH connection
        if not valid_ssh_connection(srv_address, srv_user):
            print '[WARNING]: Could not validate SSH connection.'
        
        # Write .deploy file
        config = {
            'server': {
                'address': srv_address,
                'user' : srv_user
            },
            'project': {
                'name': project,
                'preset': preset,
                'directories': {
                    'source': source_dir,
                    'build': build_dir
                }
            },
            'scripts': {
                'before': [],
                'test' : [],
                'after': []
            }
        }
        
        try:
            file_handle = open('.deploy', 'w+')
            json.dump(config, file_handle, sort_keys=True, indent=4, separators=(',', ': '))
        except Exception, e:
            print 'could not write\n'
            print e
        
        

    def __cmd_now(self):
        print 'now'

    def execute(self):
        self.commands[self.cmd]()
