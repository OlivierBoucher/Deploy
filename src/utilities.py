import re
from sys import stdin


def valid_address(address):
    """Validate wheter an address is a valid hostname or IP address.
    
    Args:
        address (string): The input address to validate.
    
    Returns:
        bool: Wheter the input address is valid.
    
    """
    ip_pattern = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
    host_pattern = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
    
    return ip_pattern.match(address) or host_pattern.match(address)
    

def get_string(label, default=None,  validate=None, error_msg=None):
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
        
        input = stdin.readline().rstrip('\n')
        
        if input is '' and default is not None:
            input = default
            
        if validate is None or validate(input):
            return input
        else:
            if error_msg is not None:
                print error_msg
        