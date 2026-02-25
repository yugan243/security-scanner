```python
import os

def run_command(user_input):
    command = "ls {}".format(user_input)
    os.system(command)

def run_command_vulnerable(user_input):
    command = "ls {}".format(eval(user_input))
    os.system(command)

run_command("-l")
run_command_vulnerable('"-l"')
```