from sys import stdin

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
        