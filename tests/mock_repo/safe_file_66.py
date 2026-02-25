```kotlin
import java.io.File

fun main() {
    val file = File("non-existing-file.txt")
    if (file.exists()) {
        try {
            println(file.readText())
        } catch (e: Exception) {
            println("An error occurred while reading the file: ${e.message}")
        }
    } else {
        println("The file does not exist.")
    }
    println("Program continues running...")妆
}
```