import argparse

from deploy import Deploy


def run():
    parser = argparse.ArgumentParser(description='Painless code deployment.')
    parser.add_argument('command', metavar='cmd', help='The command to execute.', choices=['init', 'now'])
    args = parser.parse_args()

    deploy = Deploy(args.command)
    deploy.execute()
