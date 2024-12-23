import os

from alx import dbg, save_text_to_file, save_pydata_to_json_file, read_pydata_from_json_file, is_file_exists
import sys
import re
from math import *
from numpy import *
from pprint import pprint
import numpy as np

vars_dict=dict()
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
    global vars_dict
    vars_dict = {'$': (0.0, repr(0.0))}

def repr_vars_dict(var_dict):
    _repr_dict = dict()
    for key, value in var_dict.items():
        _repr_dict[key] = value[v_rep]
    return _repr_dict

def load_repr_dict(repr_dict):
    _vars_dict = dict()
    for key, value in repr_dict.items():
        _vars_dict[key] = (eval(value), value)
    return _vars_dict

def remove_white_spaces(s:str) -> str:
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
        _msg = 'Error: Symbol(s) ' + ','.join(check_list) + ' are not allowed in variable name.'
        return _Ok, _msg

    check_list = re.findall(r'[a-zA-Z_]', varname[0])

    if not check_list:
        _Ok = False
        _msg = 'Error: Symbol ' + f'{varname[0]}' + ' is not allowed as a first symbol of variable name.'
        return _Ok, _msg

    return _Ok, _msg

def outs(_var:str):
    if vars_dict[_var][v_rep] == str(vars_dict[_var][v_val]):
        return vars_dict[_var][v_rep]
    else:
        return type(vars_dict[_var][v_val]).__name__ + '(\n' + str(vars_dict[_var][v_val]) + '\n)'

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

def try_result_int() -> int:
    try:
        _rc = int(vars_dict['$'][v_val])
    except (ValueError, TypeError, ZeroDivisionError):
        _rc = -1
    return _rc

def try_evaluate(cmd):

    cmd = remove_white_spaces(cmd)
    try:
        out_str = evaluate_cmd(cmd)
    except Exception as err:
        out_str = str(err)

    print(f'   {out_str}')

if __name__ == "__main__":

    if is_file_exists(var_file_json):
        Ok, repr_dict = read_pydata_from_json_file(var_file_json)
        if not Ok:

            print(f'\n(!) Eval.py: Error occurred while reading {var_file_json}:')
            print(f'{vars_dict}\n')

            init_vars_dict()
        else:
            vars_dict = load_repr_dict(repr_dict)
    else:
        init_vars_dict()

    if len(sys.argv) > 1:
        cmd_str = ' '.join(sys.argv[1:])
        try_evaluate(cmd_str)
    else:
        print('>> eVal.py, Ver. 0.1')
        print(' = from math import *, from numpy import *')
        print(' = math lib help is available at: https://docs.python.org/3/library/math.html')
        print(' * Use ?v command to list all variables. Use $ variable to refer to last result')

        while True:
            cmd_str=input('>> ').strip()
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
            elif cmd_str:
                try_evaluate(cmd_str)
            else:
                print(f'-> Quit')
                break

    Ok, msg = save_text_to_file(f'@set {eval_file}={str(vars_dict['$'][v_val])}'.
                                replace('\n',' ')+'\n', cmd_file_eval)
    if not Ok:
        print(f'\n(!) Eval.py: Error occurred while saving {cmd_file_eval}:')
        print(msg)

    Ok, msg = save_text_to_file(f'@set {repr_file}={str(vars_dict['$'][v_rep])}'.
                                replace('\n',' ')+'\n', cmd_file_repr)
    if not Ok:
        print(f'\n(!) Eval.py: Error occurred while saving {cmd_file_repr}:')
        print(msg)

    Ok, msg = save_pydata_to_json_file(repr_vars_dict(vars_dict), var_file_json)
    if not Ok:
        print(f'\n(!) Eval.py: Error occurred while saving {var_file_json}:')
        print(msg)

    sys.exit(try_result_int())
