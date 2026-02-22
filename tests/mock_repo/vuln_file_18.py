```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Enter your username:");
        String username = scanner.nextLine();

        System.out.println("Enter your password:");
        String password = scanner.nextLine();

        // Vulnerability: Sensitive information such as password is logged using System.out.println()
        System.out.println("User " + username + " entered password: " + password);
    }
}
```