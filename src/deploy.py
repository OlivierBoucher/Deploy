import os
from utilities import get_string

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
        #   Server user
        

    def __cmd_now(self):
        print 'now'

    def execute(self):
        self.commands[self.cmd]()
