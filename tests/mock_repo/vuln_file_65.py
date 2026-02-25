```python
import os

def run_command(user_input):
    command = "ls " + user_input
    os.system(command)

def run_eval(user_input):
    eval(user_input)

if __name__ == "__main__":
    user_input = input("Enter your command: ")
    run_command(user_input)
    run_eval(user_input)
```