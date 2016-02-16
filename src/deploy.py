from utilities import get_string

class Deploy(object):
    def __init__(self, command, config):
        self.cmd = command
        self.config = config
        self.commands = {
            'init': self.__cmd_init,
            'now': self.__cmd_now,
        }

    def __cmd_init(self):
        # testing utilities
        # test = get_string('Enter your name', default='Olivier', validate=lambda x: True, error_msg='HH')
        
        # Local info
        #   Project name, default to current dir
        #   Preset, must choose from available presets
        #   Source dir
        #   Build dir
        
        # Remote
        #   Server address
        #   Server user
        

    def __cmd_now(self):
        print 'now'

    def execute(self):
        self.commands[self.cmd]()
