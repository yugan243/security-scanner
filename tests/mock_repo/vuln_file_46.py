```kotlin
import java.util.*

class VulnerableClass {
    fun getValue(map: HashMap<String, Any>, key: String): Any? {
        return map[key]
    }
}

fun main() {
    val map = HashMap<String, Any>()
    map["key"] = 123

    val vc = VulnerableClass()
    val value = vc.getValue(map, "key")
    val castedValue = value as String // This will throw ClassCastException if value is not a String

    println(castedValue)
}
```