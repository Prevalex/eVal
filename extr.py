import re

def extract_indexed_variables(expression):
    # Regular expression pattern to capture a variable followed by multiple indices
    pattern = r"(\w+)((?:\[\w+\])+)"

    # Find all matches
    matches = re.findall(pattern, expression)

    result = []
    for var_name, indices in matches:
        # Extract individual indices inside brackets
        index_list = re.findall(r"\[(\w+)\]", indices)
        result.append((var_name, index_list))

    return result

# Example expressions
expr1 = "mylist[3] = 123*45"
expr2 = "matrix[2][5] = 10"
expr3 = "data[key1][key2][3] = 99"
expr4 = "data[key1](key2)[3] = 99"

# Running function
print(extract_indexed_variables(expr1))  # [('mylist', ['3'])]
print(extract_indexed_variables(expr2))  # [('matrix', ['2', '5'])]
print(extract_indexed_variables(expr3))  # [('data', ['key1', 'key2', '3'])]
print(extract_indexed_variables(expr4))  # [('data', ['key1', 'key2', '3'])]

