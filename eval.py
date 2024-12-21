import sys
import re
from math import *
from numpy import *
import numpy as np

vars_dict=dict()
vars_dict['$'] = 0.0  # $ can be used as last result (result of last evaluation)

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
            part_list[index] = repr(vars_dict[part_list[index]])

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
    vars_dict['$'] = _result

    if _var_name:
        vars_dict[_var_name] = _result
        _out_str += (_var_name + ' = ')

    # compile _out_str for printing
    if _eval_str == _cmd_str:
        if _var_name:
            _out_str += (repr(_result))
        else:
            _out_str += (_cmd_str + ' = ' + repr(_result))

    else:
        if _cmd_str in vars_dict:
            _out_str += (_cmd_str + ' = ' + repr(_result))  # str for numpy
        else:
            _out_str += (_cmd_str+' = ' + _eval_str + ' = ' + repr(_result))

    return _out_str

def try_result_int() -> int:
    try:
        _rc = int(vars_dict['$'])
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

    if len(sys.argv) > 1:
        cmd_str = ' '.join(sys.argv[1:])
        try_evaluate(cmd_str)
        print('=')
        #print(f'{eval(repr(vars_dict['$']))}')
        print(f'{vars_dict['$']}')
        sys.exit(try_result_int())

    else:
        print('>> eVal.py, Ver. 0.1')
        print(' = from math import *, from numpy import *')
        print(' = math lib help is available at: https://docs.python.org/3/library/math.html')
        print(' * Use ?v command to list all variables. Use $ variable to refer to last result')

        while True:
            cmd_str=input('>> ').strip()
            if cmd_str == '?v':
                for itm in vars_dict:
                    print(f'   {itm} = {repr(vars_dict[itm])}')
            elif cmd_str == '?' or cmd_str == '?$':
                print(vars_dict['$'])
            elif len(cmd_str)> 1:
                if cmd_str[0] == '?':
                    if cmd_str[1:] in vars_dict:
                        print(vars_dict[cmd_str[1:]])
            elif cmd_str:
                try_evaluate(cmd_str)
            else:
                print(f'-> Quit')
                sys.exit(try_result_int())
