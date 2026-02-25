```python
def vulnerable_function(user_input):
    if not isinstance(user_input, str):
        raise ValueError('Invalid input type. Expected string.')
    msg = f"Hello, {user_input}!"
    print(msg)

vulnerable_function("Attacker")
```