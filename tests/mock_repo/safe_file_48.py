```python
import subprocess

def run_command(user_input):
    try:
        command = user_input.split()
        subprocess.run(command, check=True)
    except Exception as e:
        print(f"An error occurred: {e}")

run_command(input("Enter your command: "))
```