```java
import java.io.*;

public class Main {
    public static void main(String[] args) {
        try {
            ByteArrayOutputStream byteOut = new ByteArrayOutputStream();
            ObjectOutputStream out = new ObjectOutputStream(byteOut);
            out.writeObject(new VulnerableClass());
            byte[] bytes = byteOut.toByteArray();

            ByteArrayInputStream byteIn = new ByteArrayInputStream(bytes);
            ObjectInputStream in = new ObjectInputStream(byteIn);
            Object obj = in.readObject();

            System.out.println(obj);
        } catch (Exception e) {
            e.printStackTrace(); inclusion of the vulnerability
        }
    }
}

class VulnerableClass implements Serializable {
    private void readObject(ObjectInputStream in) throws Exception {
        Runtime.getRuntime().exec("calc");
    }
}
```