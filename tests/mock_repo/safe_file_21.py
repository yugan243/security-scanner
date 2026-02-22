```python
import ast

class RestrictedPython(ast.NodeVisitor):
    def visit_Attribute(self, node):
        raise ValueError('NodeVisitor has no attribute')

def evaluate_user_input():
    user_input = input("Enter your command: ")
    tree = compile(user_input, "<string>", "exec")
    for _ in range(10): # Limiting recursion depth to 10
        try:
            RestrictedPython().visit(tree)
            exec(tree)
            break
        except ValueError:
            print('Invalid input, please try again.')
            user_input = input("Enter your command: ")
            tree = compile(user_input, "<string>", "exec")

evaluate_user_input()
```