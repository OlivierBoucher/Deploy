import jsonschema
import re
import getpass
import os
import ConfigParser
import StringIO
from importlib import import_module

from sys import stdin

from terminal import Terminal


# TODO(Olivier): remove this function and store the scripts in memory.
def get_bash_script(script):
    with open('bash/%s.sh' % script, 'r') as file_handle:
        script = file_handle.read()
        return script


def get_supervisor_config(config, preset):
    user = config['server']['user']
    project = config['project']['name']
    supervisor_config = ConfigParser.RawConfigParser()
    section = 'program:%s' % project

    supervisor_config.add_section(section)
    supervisor_config.set(section, 'command', preset.get_run_cmd())
    supervisor_config.set(section, 'autostart', 'true')
    supervisor_config.set(section, 'autorestart', 'true')
    supervisor_config.set(section, 'startretries', '10')
    supervisor_config.set(section, 'user', user)
    supervisor_config.set(section, 'directory', '/home/%s/.deploy/%s' % (user, project))
    supervisor_config.set(section, 'redirect_stderr', 'true')
    supervisor_config.set(section, 'stdout_logfile', '/var/log/supervisor/%s.log' % project)
    supervisor_config.set(section, 'stdout_logfile_maxbytes', '50MB')
    supervisor_config.set(section, 'stdout_logfile_backups', '10')
    supervisor_config.set(section, 'environment', preset.get_environment_vars())

    output = StringIO.StringIO()
    supervisor_config.write(output)

    return output.getvalue()


def load_preset(preset):
    language = preset.split(':')[0]
    subset = preset.split(':')[1]
    preset_class = '%s%sPreset' % (language.capitalize(), subset.capitalize())
    py_module = import_module('.presets.%s.%s' % (language, subset), __package__)

    if hasattr(py_module, preset_class):
        return getattr(py_module, preset_class)


def get_installed_presets():
    presets_path = 'app/presets'
    presets = []

    for language in os.listdir(presets_path):
        if os.path.isdir('%s/%s' % (presets_path, language)):
            for subset_file in os.listdir('%s/%s' % (presets_path, language)):
                if os.path.isfile('%s/%s/%s' % (presets_path, language, subset_file)):
                    subset = os.path.splitext(subset_file)[0]
                    if not subset.startswith('_'):
                        presets.append('%s:%s' % (language, subset))

    return presets


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


def get_string(label, default=None, validate=None, error_msg=None, password=False):
    """Gets the desired string from stdin.
    
    Args:
        label (string): The label presented to the user.
        default (Optional[str]): The default value. Defaults to None.
        validate (Optional[lambda]): The function used to validate the input. Defaults to None.
        error_msg (Optional[str]): The error message shown to the user. Defaults to None.
        password (Optional[bool]): If the input must be masked.
    
    Returns:
        string: User selected value or default.
    
    """
    while True:
        print label if default is None else label + ' (' + default + ')'

        if not password:
            input_txt = stdin.readline().rstrip('\n')
        else:
            input_txt = getpass.getpass()

        if input_txt == '' and default is not None:
            input_txt = default

        if validate is None or validate(input_txt):
            return input_txt
        else:
            if error_msg is not None:
                print error_msg
