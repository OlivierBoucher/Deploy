import argparse

from deploy import Deploy

from server import Server

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Painless code deployment.')
    parser.add_argument('command', metavar='cmd', help='The command to execute.', choices=['init', 'now'])
    args = parser.parse_args()

    s = Server('streamcenterapp.com', 'olivier')
    print s._get_package_manager()

    #deploy = Deploy(args.command)
    #deploy.execute()
