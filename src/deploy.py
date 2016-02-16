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
        # testing utilities
        # test = get_string('Enter your name', default='Olivier', validate=lambda x: True, error_msg='HH')
        
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
            error_msg='The selected preset does not exist. Please refer to this list:\n\t- ' + presets_list
            )
        
        #   Source dir
        #   Build dir
        
        # Remote
        #   Server address
        #   Server user
        

    def __cmd_now(self):
        print 'now'

    def execute(self):
        self.commands[self.cmd]()
