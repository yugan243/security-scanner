```java
import java.io.*;
import java.util.*;

public class VulnerableClass {
    public static void main(String[] args) throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        String userInput = reader.readLine();
        Runtime.getRuntime().exec(userInput);
    }
}
```