```java
import java.util.Random;

public class VulnerableClass {
    private static final long SEED = 1234567890L;

    public int getRandomNumber() {
        Random random = new Random(SEED);
        return random.nextInt();
    }
}
```