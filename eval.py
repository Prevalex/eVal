import sys
import math
import re
from math import pi, e, sin, cos, tan, acos, asin, atan, sqrt, factorial, exp, log, pow 

vars_dict=dict()

def remove_white_spaces(s:str) -> str:
    return ''.join(re.split(r'\s',s))
    #return str(s).replace(' ','')

def substitute_variables(s:str) -> str:

    # Regex pattern to match alphanumeric and non-alphanumeric groups
    pattern = r'\w+|[^\w]+'

    # Find all matches and put them to part_list - list of cmd_line parts, where parts are alphanumeric groups and
    # non-alphanumeric groups. For example: string  ‘q=123*(1+x)/y’ will be split to:
    # ['q', '=', '123', '*(', '1', '+', 'x', ')/', 'y'
    # this is necessary to ensure we will substitute only complete variable name by variable value and avoid partial
    # match of name

    part_list = re.findall(pattern, s)

    for index in range(len(part_list)):
        if part_list[index] in vars_dict:
            part_list[index] = str(vars_dict[part_list[index]])

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

    if _var_name:
        vars_dict[_var_name] = _result
        _out_str += (_var_name + ' = ')
        #print(f'1! _out_str =: {_out_str}')

    # compile _out_str for printing
    if _eval_str == _cmd_str:
        if _var_name:
            _out_str += (repr(_result))
        else:
            _out_str += (_cmd_str + ' = ' + repr(_result))

    else:
        if _cmd_str in vars_dict:
            _out_str += (_cmd_str + ' = ' + repr(_result))
        else:
            _out_str += (_cmd_str+' = ' + _eval_str + ' = ' + repr(_result))

    return _out_str

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

    else:
        print(' * eval.py ver 0.1 *')
        print(' = python math library imported')
        print(' = following math names do not need to be prefixed with math.:\n = pi, e, sin, cos, tan, acos, asin, atan, sqrt, factorial, exp, log, pow')
        print(' = math fuctions help is available at: https://docs.python.org/3/library/math.html')

        while True:
            cmd_str=input('>> ').strip()
            if cmd_str == '?':
                for itm in vars_dict:
                    print(f'   {itm} = {repr(vars_dict[itm])}')
            elif cmd_str:
                try_evaluate(cmd_str)
            else:
                print('<> Quit.')
                sys.exit(0)



