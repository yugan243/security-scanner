```java
import java.io.*;

public class Main {
    public static void main(String[] args) throws Exception {
        String str = "Hello, World!";
        byte[] bytes = str.getBytes(); // This line can cause a buffer overflow if no charset is specified
        FileOutputStream fos = new FileOutputStream("output.txt");
        fos.write(bytes);
        fos.close();
    }
}
```