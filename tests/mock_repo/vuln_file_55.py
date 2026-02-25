```java
import java.util.concurrent.atomic.AtomicInteger;

public class Main {
    private static final AtomicInteger nextId = new AtomicInteger(0);

    // Incorrect use of ThreadLocal variable
    private static final ThreadLocal<Integer> threadId = new ThreadLocal<Integer>() {
        protected Integer initialValue() {
            return nextId.getAndIncrement();
        }
    };

    public static void main(String[] args) {
        new Thread(() -> System.out.println("Thread " + threadId.get())).start();
        new Thread(() -> System.out.println("Thread " + threadId.get())).start();
    }
}
```