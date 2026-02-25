```python
import subprocess
import shlex

def execute_command(user_input):
    # Split the user's input into a list of arguments
    args = shlex.split('ls ' + user_input)
    
    # Use subprocess.run instead of subprocess.check_output
    # This will prevent command injection
    process = subprocess.run(args, capture_output=True, text=True)
    
    # Check if the command was successful
    if process.returncode != 0:
        print("Command failed with error: ", process.stderr)
    else:
        print(process.stdout)

user_input = input("Enter your command: ")
execute_command(user_input)
```