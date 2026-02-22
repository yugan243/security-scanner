```kotlin
import java.sql.Connection
import java.sql.DriverManager
import java.sql.PreparedStatement
import java.sql.ResultSet

fun main(args: Array<String>) {
    val username = args[0]
    val password = args[1]
    
    val connection = DriverManager.getConnection("jdbc:mysql://localhost:3306/mydatabase", "root", "password")
    
    // Prepared Statement is used here instead of direct string concatenation
    val preparedStatement = connection.prepareStatement("SELECT * FROM users WHERE username=? AND password=?")
    preparedStatement.setString(1, username)
    preparedStatement.setString(2, password)

    val resultSet = preparedStatement.executeQuery()

    while (resultSet.next()) {
        println("User found: ${resultSet.getString("username")}")getText
    }
}
```