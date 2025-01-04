import os
from alx import dbg, save_text_to_file, save_pydata_to_json_file, read_pydata_from_json_file, is_file_exists
import sys
import re
from math import *
from numpy import *
import numpy as np
from fractions import Fraction
from colorama import Fore, Back, Style, init
init()

vars_dict:dict = dict()

v_val = 0 # index of variable value in variable tuple in vars_dict
v_rep = 1 # index of variable value in variable repr  in vars_dict

temp_folder = os.environ['TEMP']
eval_file = '$eval.value'
repr_file = '$eval.repr'
json_file =  '$eval.vars'

cmd_file_eval = os.path.join(temp_folder, eval_file+'.cmd')
cmd_file_repr = os.path.join(temp_folder, repr_file+'.cmd')
var_file_json = os.path.join(temp_folder, json_file+'.json')

def init_vars_dict():
    """
    Initializes a dictionary of variables
    :return:
    """
    global vars_dict
    vars_dict = {'$': (None, repr(None))}

def make_repr_dict(vars_dic):
    """
    Converts a dictionary of variables containing values and reprs into a dictionary of reprs only for subsequent
     saving to a .json file, i.e: {var_name: (var_value, repr(var_value))} -> {var_name: repr(var_value)}
    :param vars_dic: dictionary of variables containing their values and reprs
    :return: dictionary of variables containing their reprs only
    """
    _repr_dict = dict()
    for key, value in vars_dic.items():
        _repr_dict[key] = value[v_rep]
    return _repr_dict

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
            _vars_dict[key] = (eval(value), value)
        except Exception as err:
            _vars_dict[key] = (None, repr(None))
            print(f'\n! Eval.py: Error occurred while reading {var_file_json}:')
            print(f': {err}\n')
    _vars_dict['$'] = (None, repr(None))
    return _vars_dict

def remove_white_spaces(s:str) -> str:
    """
    Removes all white characters from a string
    :param s: input string, which may contain white characters
    :return: output string, where all white characters are removed
    """
    return ''.join(re.split(r'\s',s))

def substitute_variables(s:str) -> str:

    # Regex pattern to match alphanumeric and non-alphanumeric groups
    pattern = r'\$+|\w+|[^\w^$]+'

    # Find all matches and put them to part_list - list of cmd_line parts, where parts are alphanumeric groups and
    # non-alphanumeric groups. For example: string  ‘q=123*(1+x)/y’ will be split to:
    # ['q', '=', '123', '*(', '1', '+', 'x', ')/', 'y'
    # this is necessary to ensure we will substitute only complete variable name by variable value and avoid partial
    # match of name

    part_list = re.findall(pattern, s)

    for index in range(len(part_list)):
        if part_list[index] in vars_dict:
            part_list[index] = vars_dict[part_list[index]][v_rep]

    return ''.join(part_list)

def verify_var_name(varname:str) -> [bool, str]:
    _Ok, _msg = True, ''

    check_list = re.findall(r'\W+', varname)

    if check_list:
        _Ok = False
        _msg = 'Error: Symbol(s) \"' + '\", \"'.join(check_list) + f'\" are not allowed in variable name: \"{varname}\".'
        return _Ok, _msg

    check_list = re.findall(r'[a-zA-Z_]', varname[0])

    if not check_list:
        _Ok = False
        _msg = (Fore.RED + 'Error: Symbol ' + f'{varname[0]}' + ' is not allowed as a first symbol of variable name.' +
                Fore.RESET)
        return _Ok, _msg

    return _Ok, _msg

def outs(_var:str):
    if vars_dict[_var][v_rep] == str(vars_dict[_var][v_val]):
        return vars_dict[_var][v_rep]
    elif type(vars_dict[_var][v_val]).__name__ == 'str':
        return vars_dict[_var][v_rep]
    else:
        return (type(vars_dict[_var][v_val]).__name__ + '(\n' + Style.BRIGHT + str(vars_dict[_var][v_val]) +
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

    if _var_name:
        # Got assignment
        _Ok, _msg = verify_var_name(_var_name)

        if not _Ok:
            raise ValueError(_msg)

    _eval_str = substitute_variables(_cmd_str)
    _result = eval(_eval_str)
    vars_dict['$'] = (_result, repr(_result))

    if _var_name:
        vars_dict[_var_name] = (_result, repr(_result))
        _out_str += (_var_name + ' = ')

    # compile _out_str for printing
    if _eval_str == _cmd_str:
        if _var_name:
            _out_str += outs(_var_name)
        else:
            _out_str += (_cmd_str + ' = ' + outs('$'))
    else:
        if _cmd_str in vars_dict:
            _out_str += (_cmd_str + ' = ' + outs(_cmd_str))
        else:
            _out_str += (_cmd_str + ' = ' + _eval_str + ' = ' + outs('$'))

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
            print(f'   {itm} = {outs(itm)}')
    elif cmd_str == '-v':
        init_vars_dict()
    else:
        parsed_flag = False
    return parsed_flag

if __name__ == "__main__":

    if is_file_exists(var_file_json):
        Ok, repr_dict = read_pydata_from_json_file(var_file_json)
        if not Ok:

            print(Fore.RED)
            print(f'\n! Eval.py: Error occurred while reading {var_file_json}:')
            print(f': {vars_dict}\n')
            print(Fore.RESET)

            init_vars_dict()
        else:
            vars_dict = load_repr_dict(repr_dict)
    else:
        init_vars_dict()

    if len(sys.argv) > 1:
        cmdline = ' '.join(sys.argv[1:])
        if not cmd_keywords_found(cmdline):
            try_evaluate(cmdline)
    else:
        print('>> eVal.py, Ver. 0.1')
        print(' = from math import *, from numpy import *')
        print(' = math lib help is available at: https://docs.python.org/3/library/math.html')
        print(' * Use ?v command to list all variables. Use $ variable to refer to last result')

        while True:
            cmdline=input('>> ').strip()
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
        print(f'\n! Eval.py: Error occurred while saving {cmd_file_eval}:')
        print(f': {msg}')
        print(Fore.RESET)

    Ok, msg = save_text_to_file(create_cmd_set(vars_dict,v_rep, repr_file), cmd_file_repr)
    if not Ok:
        print(Fore.RED)
        print(f'\n! Eval.py: Error occurred while saving {cmd_file_repr}:')
        print(f': {msg}')
        print(Fore.RESET)

    Ok, msg = save_pydata_to_json_file(make_repr_dict(vars_dict), var_file_json)
    if not Ok:
        print(Fore.RED)
        print(f'\n! Eval.py: Error occurred while saving {var_file_json}:')
        print(f': {msg}')
        print(Fore.RESET)

    sys.exit(try_result_as_int())
