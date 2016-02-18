import re, paramiko, jsonschema, json
from sys import stdin


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


def valid_ssh_connection(address, user):
    valid = False
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(address, username=user)
        valid = True
    except IOError, e:
        return False, e
    finally:
        client.close()

    return valid, None


def valid_config(config_json):
    """ Validates the configuration file against the required schema

    Args:
        config_json (string): The config, as a JSON string

    Returns:
        bool: whether the config is valid

    """
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "id": "/",
        "properties": {
            "server": {
                "id": "server",
                "type": "object",
                "properties": {
                    "address": {
                        "id": "address",
                        "type": "string"
                    },
                    "user": {
                        "id": "user",
                        "type": "string"
                    }
                }
            },
            "project": {
                "id": "project",
                "type": "object",
                "properties": {
                    "name": {
                        "id": "name",
                        "type": "string"
                    },
                    "preset": {
                        "id": "preset",
                        "type": "string"
                    },
                    "directories": {
                        "id": "directories",
                        "type": "object",
                        "properties": {
                            "source": {
                                "id": "source",
                                "type": "string"
                            },
                            "build": {
                                "id": "build",
                                "type": "string"
                            }
                        }
                    }
                }
            },
            "scripts": {
                "id": "scripts",
                "type": "object",
                "properties": {
                    "before": {
                        "id": "before",
                        "type": "array",
                        "items": {}
                    },
                    "after": {
                        "id": "after",
                        "type": "array",
                        "items": {}
                    }
                }
            }
        },
        "required": [
            "server",
            "project",
            "scripts"
        ]
    }
    validator = jsonschema.Draft4Validator(schema=schema,
                                           types={"object": dict})

    for error in sorted(validator.iter_errors(config_json.replace('\n', ' ')), key=str):
        Terminal.print_error(error.message)
        return False

    return True


def valid_address(address):
    """Validate whether an address is a valid hostname or IP address.
    
    Args:
        address (string): The input address to validate.
    
    Returns:
        bool: Whether the input address is valid.
    
    """
    ip_pattern = re.compile(
        "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
    host_pattern = re.compile(
        "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")

    return ip_pattern.match(address) or host_pattern.match(address)


def get_string(label, default=None, validate=None, error_msg=None):
    """Gets the desired string from stdin.
    
    Args:
        label (string): The label presented to the user.
        default (Optional[str]): The default value. Defaults to None.
        validate (Optional[lambda]): The function used to validate the input. Defaults to None.
        error_msg (Optional[str]): The error message shown to the user. Defaults to None.
    
    Returns:
        string: User selected value or default.
    
    """
    while True:
        print label if default is None else label + ' (' + default + ')'

        input_txt = stdin.readline().rstrip('\n')

        if input_txt is '' and default is not None:
            input_txt = default

        if validate is None or validate(input_txt):
            return input_txt
        else:
            if error_msg is not None:
                print error_msg
