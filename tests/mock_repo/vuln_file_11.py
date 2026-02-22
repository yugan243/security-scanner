```kotlin
import java.sql.Connection
import java.sql.DriverManager
import java.sql.PreparedStatement

fun main(args: Array<String>) {
    val username = "user"
    val password = "pass"
    val connectionProps = Properties()
    connectionProps["user"] = username
    connectionProps["password"] = password
    val connUrl = "jdbc:mysql://localhost:3306/database"
    val conn = DriverManager.getConnection(connUrl, connectionProps)
    val sql = "SELECT * FROM users WHERE username = '${args[0]}' AND password = '${args[1]}'"
    val statement = conn.prepareStatement(sql)
    val resultSet = statement.executeQuery()
    while (resultSet.next()) {
        println("User found: ${resultSet.getString("username")}")
    }
}
```