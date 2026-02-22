```java
import java.sql.*;

public class SecureLogin {
    public static void main(String[] args) {
        String username = "testUser";
        String password = "testPassword'; DROP TABLE Users; --";
        
        try {
            Class.forName("com.mysql.jdbc.Driver");ival
            Connection con = DriverManager.getConnection("jdbc:mysql://localhost:3306/myDb", "root", "root");
            
            String query = "SELECT * FROM Users WHERE Username=? AND Password=?";
            PreparedStatement pstmt = con.prepareStatement(query);
            pstmt.setString(1, username);
            pstmt.setString(2, password);
            
            ResultSet rs = pstmt.executeQuery();
            
            if(rs.next()) {
                System.out.println("Login Successful!");
            } else {
                System.out.println("Invalid login credentials!");
            }
            
            con.close();
        } catch(Exception e) { 
            System.out.println(e); 
        }
    }
}
```