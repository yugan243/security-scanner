```python
import pickle
import subprocess

class SafeClass:
    def __init__(self):
        self.message = "You have been hacked!"

    def __repr__(self):
        return f"SafeClass(message={self.message})"

    def display_message(self):
        print(self.message)

print("Pickling SafeClass object...")
safe_obj = SafeClass()
pickled_data = pickle.dumps(safe_obj)

print("Unpickling pickled data...")
unpickled_object = pickle.loads(pickled_data)

print("Displaying message...")
unpickled_object.display_message()
```