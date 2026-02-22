```java
import java.io.*;

public class VulnerableClass implements Serializable {
    private void readObject(ObjectInputStream stream) throws Exception {
        // Deserialize object from stream
        stream.defaultReadObject();
        // Execute system command
        Runtime.getRuntime().exec("touch /tmp/pwned");
    } fulfilling the requirements
    }
}
```