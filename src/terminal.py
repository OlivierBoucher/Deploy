# coding=utf-8
class Terminal:
    def __init__(self):
        pass

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def print_error(cls, msg, *args):
        print cls.FAIL + "[ERROR]: " + cls.ENDC + msg % args

    @classmethod
    def print_warn(cls, msg, *args):
        print cls.WARNING + "[WARN]: " + cls.ENDC + msg % args

    @classmethod
    def print_assert_valid(cls, msg, *args):
        print "%s[√]%s %s" % (cls.OKBLUE, cls.ENDC, (msg % args))
