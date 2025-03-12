import os
from alx import ppdbg, dbg, save_text_to_file, save_pydata_to_json_file, read_pydata_from_json_file, is_file_exists
import sys
import re
import math as ma
import numpy as np
from numpy import array

from colorama import Fore, Back, Style, just_fix_windows_console
#from prompt_toolkit.key_binding.bindings.named_commands import end_of_line
just_fix_windows_console()

""" #https://pypi.org/project/colorama/
colorama_dic = {'Fore': ['BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE', 'RESET',
                         #These are fairly well supported, but not part of the standard:
                         'LIGHTBLACK_EX', 'LIGHTRED_EX', 'LIGHTGREEN_EX', 'LIGHTYELLOW_EX', 'LIGHTBLUE_EX',
                         'LIGHTMAGENTA_EX', 'LIGHTCYAN_EX', 'LIGHTWHITE_EX'],

                'Back': ['BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE', 'RESET',
                         #These are fairly well supported, but not part of the standard:
                         'LIGHTBLACK_EX', 'LIGHTRED_EX', 'LIGHTGREEN_EX', 'LIGHTYELLOW_EX', 'LIGHTBLUE_EX',
                         'LIGHTMAGENTA_EX', 'LIGHTCYAN_EX', 'LIGHTWHITE_EX'],

                'Style': ['DIM', 'NORMAL', 'BRIGHT', 'RESET_ALL']
                }
"""
vars_dict:dict = dict()

v_val = 0 # index of variable value in variable tuple in vars_dict
v_rep = 1 # index of variable value in variable repr  in vars_dict

temp_folder = os.environ['TEMP']
eval_file = '$eVal.value'
repr_file = '$eVal.repr'
json_file = '$eVal.vars'

# Variables whose names are stored in key_vars list are not included in the globals() globals,
# and when expressions are evaluated, their names are replaced by their repr() representation
# before evaluation.
key_vars = ['$']  #special internal variables (with special meaning)

cmd_file_eval = os.path.join(temp_folder, eval_file+'.cmd')
cmd_file_repr = os.path.join(temp_folder, repr_file+'.cmd')
var_file_json = os.path.join(temp_folder, json_file+'.json')

def init_vars_dict():
    """
    Reinitializes the variable's dictionary. If the dictionary was not empty, all variables contained in it are also
    removed from globals().

    Returns:
        None
    """
    global vars_dict

    pop_list = list(vars_dict)
    for var in pop_list:
        vars_dict.pop(var, None)
        globals().pop(var, None)

    vars_dict['$'] = (None, repr(None))

def create_repr_dict(vars_dic: dict) -> dict:
    """
    Converts a vars_dict dictionary of variables containing values and reprs into a dictionary of reprs only
    for subsequent saving to a .json file, i.e: {var_name: (var_value, repr(var_value))} -> {var_name: repr(var_value)}

    Args:
        vars_dic: dictionary of variables containing their values and reprs

    Returns:
        dictionary of variables containing their reprs only
    """

    _repr_dict = dict()
    for key, value in vars_dic.items():
        _repr_dict[key] = value[v_rep]
    return _repr_dict

def set_var(var_name:str, var_value:any) -> [bool, str]:
    """
    Creates a variable with the given value.

    Creating a variable involves inserting the variable name and value/representation into the vars_dic dictionary.
    Also, if the variable name is not specified in the key_vars list, the variable is inserted into the globals().

    Args:
        var_name: name of the variable
        var_value: value of the variable

    Returns:
        tuple (_Ok, _msg): If an error occurred, _Ok=False, _msg=error message. Otherwise (success) returns (True, '')
    """
    _Ok, _msg = True, ""

    if var_name in key_vars:
        vars_dict[var_name] = (var_value, repr(var_value))
    else:
        if var_name in vars_dict:
            vars_dict[var_name]=(var_value, repr(var_value))
            globals()[var_name] = var_value
        elif (var_name in globals()) or (var_name in locals()):
            _Ok = False
            _msg = f'{Fore.RED}Error: variable/object "{var_name}" is reserved and cannot be redefined {Fore.RESET}'
        else:
            vars_dict[var_name] = (var_value, repr(var_value))
            globals()[var_name] = var_value

    return _Ok, _msg

def verify_var_name(var_name:str) -> [bool, str]:
    _Ok, _msg = True, ''

    check_list = re.findall(r'\W+', var_name)

    if check_list:
        _Ok = False
        _msg = 'Error: Symbol(s) \"' + '\", \"'.join(check_list) + f'\" are not allowed in variable name: \"{var_name}\".'
        return _Ok, _msg

    check_list = re.findall(r'[a-zA-Z_]', var_name[0])

    if not check_list:
        _Ok = False
        _msg = (Fore.RED + 'Error: Symbol ' + f'{var_name[0]}' + ' is not allowed as a first symbol of variable name.' +
                Fore.RESET)
        return _Ok, _msg

    # verify if the variable is not reserved.
    if var_name in vars_dict:
        return _Ok, _msg

    elif (var_name in globals()) or (var_name in locals()):
        _Ok = False
        _msg = f'{Fore.RED}Error: variable/object "{var_name}" is reserved and cannot be redefined {Fore.RESET}'
        return _Ok, _msg

    return _Ok, _msg

def load_repr_dict(repr_dic):
    """
    Converts a dictionary of variables containing reprs only into a dictionary of values and reprs for subsequent
     use as variable deposit. I.e.: {var_name: repr(var_value)} -> {var_name: (var_value, repr(var_value))}.
     * Uses eval() to convert repr(var_value) to var_value
    :param repr_dic:
    :return: dictionary of variables containing their reprs only - like {var_name: (var_value, repr(var_value))}
    """
    _vars_dict = dict()
    for key, value in repr_dic.items():
        try:
            set_var(key, eval(value))
        except Exception as err:
            set_var(key, None)
            print(f'\n! Eval.py: Error occurred while reading {var_file_json}:')
            print(f': {err}\n')
    set_var('$', None)
    return _vars_dict

def remove_white_spaces(s:str) -> str:
    """
    Removes all white characters from a string
    :param s: input string, which may contain white characters
    :return: output string, where all white characters are removed
    """
    return ''.join(re.split(r'\s',s))

def substitute_variables(expression:str) -> str:

    # Regex pattern to match alphanumeric and non-alphanumeric groups
    pattern = r'\$+|\w+|[^\w^$]+'

    # Find all matches and put them to part_list - list of cmd_line parts, where parts are alphanumeric groups and
    # non-alphanumeric groups. For example: string  ‘q=123*(1+x)/y’ will be split to:
    # ['q', '=', '123', '*(', '1', '+', 'x', ')/', 'y'
    # this is necessary to ensure we will substitute only complete variable name by variable value and avoid partial
    # match of name

    part_list = re.findall(pattern, expression)

    for index in range(len(part_list)):
        if part_list[index] in vars_dict:
            if part_list[index] not in globals():
                part_list[index] = vars_dict[part_list[index]][v_rep]

    return ''.join(part_list)

def var_output(_var:str):
    if vars_dict[_var][v_rep] == str(vars_dict[_var][v_val]):
        return Style.BRIGHT + Fore.CYAN + vars_dict[_var][v_rep] + Style.RESET_ALL
    elif type(vars_dict[_var][v_val]).__name__ == 'str':
        return Style.BRIGHT + Fore.CYAN + vars_dict[_var][v_rep] + Style.RESET_ALL
    else:
        return (type(vars_dict[_var][v_val]).__name__ + '(\n' + Style.BRIGHT + Fore.CYAN + str(vars_dict[_var][v_val]) +
                Style.RESET_ALL + '\n)')

def parse_assignment(s:str):
    pos=s.find('=')
    if pos >= 0:
        return s[:pos], s[pos+1:]
    else:
        return '', s
        
def evaluate_cmd(_cmd_str: str) -> str:
    _out_str = ''

    _var_name, _cmd_str = parse_assignment(_cmd_str)

    if _var_name:  # Got assignment
        _Ok, _msg = verify_var_name(_var_name)

        if not _Ok:
            raise ValueError(_msg)

    _eval_str = substitute_variables(_cmd_str)
    _result = eval(_eval_str)
    vars_dict['$'] = (_result, repr(_result))

    # assign value to variable
    if _var_name:
        set_var(_var_name, _result)
        _out_str += (_var_name + ' = ')

    # compile _out_str for printing
    if _eval_str == _cmd_str:
        if _var_name:
            _out_str += var_output(_var_name)
        else:
            _out_str += (_cmd_str + ' = ' + var_output('$'))
    else:
        if _cmd_str in vars_dict:
            _out_str += (_cmd_str + ' = ' + var_output(_cmd_str))
        else:
            _out_str += (_cmd_str + ' = ' + _eval_str + ' = ' + var_output('$'))

    return _out_str

def try_result_as_int() -> int:
    try:  # Try direct convert to int
        _rc = int(vars_dict['$'][v_val])
    except (ValueError, TypeError, ZeroDivisionError):
        _rc = -1
    return _rc

def try_evaluate(cmd):

    cmd = remove_white_spaces(cmd)
    try:
        out_str = evaluate_cmd(cmd)
    except Exception as err:
        out_str = Fore.RED + str(err) + Fore.RESET

    print(f'   {out_str}')

def create_cmd_set(var_dict, index, prefix):
    cmd_set = list()
    for key, value in var_dict.items():
        cmd_set.append(f'@set {prefix}.{key}={value[index]}'.replace('\n', ' '))
    return '\n'.join(cmd_set) + '\n'

def eval_help():
    hlp = """
    The eVal utility can evaluate expressions using the following Python libraries: math, numpy, re, sys, os
    To access functions and values of these libraries, use the prefixes ma., .np., re., sys., os. respectively
    For example: np.exp(ma.pi) evaluates e to the power of pi (e**pi).

    Help for the libraries is available at:
    https://docs.python.org/3/library/math.html
    https://docs.python.org/3/library/re.html
    https://docs.python.org/3/library/sys.html
    https://docs.python.org/3/library/os.html
    https://numpy.org/

    Commands:

    ?   - this help
    ?v  - list of variables and their values
    -v  - clear the list of variables
    $   - the result of the last evaluation. You can use $ in expressions to access the result of the last evaluation.

    Commands and expressions can be passed both from the command line and interactively.

    On exit, the utility tries to convert the result to an integer type and return it to the errolevel.
    Also:
    When exiting, the utility saves the following files:

    %temp%\\$eVal.vars.json - a variable list that will be loaded the next time eVal is run.
    %temp%\\$eVal.value.cmd - a batch file containing the commands: 
        set $eVal.value.<varname>=<value> 
        where <varname> is variable name, <value> is variable value.
    %temp%\\$eVal.repr.cmd - a batch file containing the command: 
        set $eVal.value.<varname>=<repr> 
        where where <varname> is variable name, repr is the representation of variable (see the repr() Python function)
    """
    return hlp

def cmd_keywords_found(cmd_str):
    parsed_flag = True
    if cmd_str == '?*':
        print('\n  {')
        vars_dict_list = []
        for itm in vars_dict:
            vars_dict_list.append(f'   {itm}: {vars_dict[itm]}')
        print(',\n'.join(vars_dict_list))
        print('   }')
    elif cmd_str == '?v':
        for itm in vars_dict:
            print(f'   {itm} = {var_output(itm)}')
    elif cmd_str == '-v':
        init_vars_dict()
    elif any([cmd_str == '?',cmd_str == '/?', cmd_str == '-h']):
        print(eval_help())
    else:
        parsed_flag = False
    return parsed_flag

if __name__ == "__main__":

    # Load saved eval variables file, if any
    if is_file_exists(var_file_json):
        Ok, repr_dict = read_pydata_from_json_file(var_file_json)
        if not Ok:

            print(Fore.RED)
            print(f'\n! eVal.py: Error occurred while reading {var_file_json}:')
            print(f': {vars_dict}\n')
            print(Fore.RESET)

            init_vars_dict()
        else:
            load_repr_dict(repr_dict)
    else:
        init_vars_dict()

    if len(sys.argv) > 1:
        cmdline = ' '.join(sys.argv[1:])
        if not cmd_keywords_found(cmdline):
            try_evaluate(cmdline)
    else:
        print(Fore.GREEN + '>> eVal.py, Ver. 0.1' + Fore.RESET)
        print(Fore.CYAN + ' = Use ? for help' + Fore.RESET)

        while True:
            cmdline=input(Fore.GREEN + '>> ' + Fore.CYAN).strip()
            print(Fore.RESET, end='')
            if cmd_keywords_found(cmdline):
                pass
            elif cmdline:
                try_evaluate(cmdline)
            else:
                #print(f'-> Quit')
                break

    Ok, msg = save_text_to_file(create_cmd_set(vars_dict,v_val, eval_file ), cmd_file_eval)
    if not Ok:
        print(Fore.RED)
        print(f'\n! eVal.py: Error occurred while saving {cmd_file_eval}:')
        print(f': {msg}')
        print(Fore.RESET)

    Ok, msg = save_text_to_file(create_cmd_set(vars_dict,v_rep, repr_file), cmd_file_repr)
    if not Ok:
        print(Fore.RED)
        print(f'\n! eVal.py: Error occurred while saving {cmd_file_repr}:')
        print(f': {msg}')
        print(Fore.RESET)

    Ok, msg = save_pydata_to_json_file(create_repr_dict(vars_dict), var_file_json)
    if not Ok:
        print(Fore.RED)
        print(f'\n! eVal.py: Error occurred while saving {var_file_json}:')
        print(f': {msg}')
        print(Fore.RESET)

    #colorama_deinit()

    sys.exit(try_result_as_int())
