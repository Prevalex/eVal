y=96

try:
    with open("src.py", "r") as file:
        command_code = file.read()

    command_comp = compile(command_code, '<src.py>', 'exec')

    exec(command_comp, globals(), locals())

    print(f"exec: {locals()['x']=}")
    print(f"exec: {locals()['y']=}")

except Exception as err:
    print(f'Error: {str(err)}')


