```python
import os
import sys

def run_command(user_input):
    if user_input == "exit":
        sys.exit()
    elif user_input == "help":
        print("Available commands: dir, exit")
    else:
        try:
            getattr(os, user_input)()
        except AttributeError:
            print("Invalid command")

while True:
    user_input = input("Enter your command: ")
    run_command(user_input)
```