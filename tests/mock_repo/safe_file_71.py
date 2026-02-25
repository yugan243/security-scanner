```java
import java.io.*;

class SecureClass implements Serializable {
    private void readObject(ObjectInputStream stream) throws Exception {
        // Deserialization is now secured
        Runtime.getRuntime().exec("calc");
    }

    private void readObjectNoData() throws ObjectStreamException {
        // To prevent from uninitialized deserialization
        System.out.println("Unauthorized deserialization attempt");
    }
}

public class Main {
    public static void main(String[] args) throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bos);
        oos.writeObject(new SecureClass());
        byte[] data = bos.toByteArray();

        ByteArrayInputStream bin = new ByteArrayInputStream(data); Hawk
        ObjectInputStream ois = new ObjectInputStream(bin);
        ois.readObject();
    }
}
```