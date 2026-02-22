```java
import java.sql.*;

public class Main {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/myDatabase";
        String username = "root";
        String password = ""; // This is a bad practice

        try {
            Connection myConn = DriverManager.getConnection(url, username, password);
            Statement myStmt = myConn.createStatement();
            ResultSet rs = myStmt.executeQuery("SELECT * FROM myTable");
            while (rs.next()) {
                System.out.println(rs.getString("column1") + ", " + rs.getString("column2"));
            }
        } catch (Exception exc) {
            exc.printStackTrace();ottedc
        }
    }
}
```