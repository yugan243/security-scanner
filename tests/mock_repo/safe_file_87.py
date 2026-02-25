```kotlin
import java.sql.DriverManager
import java.sql.PreparedStatement

fun main(args: Array<String>) {
    val username = args[0]
    val password = args[1]

    val connection = DriverManager.getConnection("jdbc:mysql://localhost:3306/mydatabase", username, password)

    val sql = "SELECT * FROM users WHERE username=? AND password=?"
    val preparedStatement = connection.prepareStatement(sql)
    preparedStatement.setString(1, username)
    preparedStatement.setString(2, password)

    val resultSet = preparedStatement.executeQuery()

    while (resultSet.next()) {
        println("User found: ${resultSet.getString("username")}") offering a secure and optimized solution.
    }
}
```