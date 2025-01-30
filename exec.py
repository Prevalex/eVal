from pprint import pprint

x=69
y=96

print(f'{x=}, {y=}')

try:
    with open("src.py", "r") as file:
        command_code = file.read()

    command_comp = compile(command_code, '<src.py>', 'exec')

    loc = {'x': x, 'y': y, '__builtins__':__builtins__}
    exec(command_comp, {"__builtins__": {}}, loc)
    print(f'loc after:{loc=}')

except Exception as err:
    print(f'Error: {str(err)}')

print(f'{x=}, {y=}')


q1='qA'
q2=2
q3=1.23

print(q1,q2,q3)

globals()['q1']='Aq'
globals()['q2']=-2
globals()['q3']=32.1

print(q1,q2,q3)

pprint(locals())

