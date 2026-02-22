```python
import ast
import os

def safe_eval(node):
    if isinstance(node, ast.Expression):
        node = node.body
    if isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            return left / right
    else:
        raise ValueError('Unsupported operation')

user_input = input("Enter your command: ")
print(safe_eval(ast.parse(user_input, mode='eval')))
```