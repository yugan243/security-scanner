```java
import java.security.SecureRandom;

public class Main {
    public static void main(String[] args) {
        SecureRandom rand = new SecureRandom();

        for (int i = 0; i < 5; i++) {
            System.out.println(rand.nextInt());
        }
    }
}
```