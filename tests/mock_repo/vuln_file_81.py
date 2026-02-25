```python
def process_input(user_input):
    buffer = bytearray(1024)
    input_length = len(user_input)
    if input_length <= len(buffer):
        buffer[:input_length] = user_input
    else:
        print("Input too long")
    return buffer

def main():
    user_input = bytearray(5000)  # This will cause a buffer overflow
    result = process_input(user_input)
    print(result)

if __name__ == "__main__":
    main()
```