import ast

try:
    with open('app.py', 'r') as f:
        ast.parse(f.read())
    print('No syntax errors found')
except SyntaxError as e:
    print(f'Syntax error at line {e.lineno}: {e.text}')
    print(f'Error message: {e.msg}')
except Exception as e:
    print(f'Other error: {e}')