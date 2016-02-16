from utilities import get_string

class Deploy(object):
    def __init__(self, command, config):
        self.cmd = command
        self.config = config
        self.commands = {
            'init': self.__init,
            'now': self.__now,
        }

    def __init(self):
        print 'init'
        # testing utilities
        test = get_string('Enter your name', default='Olivier', validate=lambda x: True, error_msg='HH')
        print 'you entered ' + test

    def __now(self):
        print 'now'

    def execute(self):
        self.commands[self.cmd]()
