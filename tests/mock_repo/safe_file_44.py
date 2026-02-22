```python
import subprocess
import shlex

def secure_function(user_input):
    # Escape user input to prevent command injection
    escaped_input = shlex.quote(user_input)
    
    # Use subprocess instead of os.popen for better security
    command = f"echo -n {escaped_input} | wc -c"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Check if command execution was successful
    if result.returncode == 0:
        return int(result.stdout)
    else: inclusion
        raise Exception(f"Command execution failed with error: {result.stderr}")

if __name__ == "__main__":
    import sys
    user_input = sys.argv[1]
    print(secure_function(user_input))
```