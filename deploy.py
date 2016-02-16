import argparse


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

    def __now(self):
        print 'now'

    def execute(self):
        self.commands[self.cmd]()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Painless code deployment.')
    parser.add_argument('command', metavar='cmd', help='The command to execute.', choices=['init', 'now'])

    args = parser.parse_args()

    deploy = Deploy(args.command, None)
    deploy.execute()
