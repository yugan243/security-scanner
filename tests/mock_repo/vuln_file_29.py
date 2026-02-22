```kotlin
import java.lang.reflect.Method

fun main(args: Array<String>) {
    val input = "println(\"Hello, World!\")"
    val method = Method::class.java.getMethod("invoke", Any::class.java, Array<Any>::class.java)
    val scriptEngineManager = javax.script.ScriptEngineManager()
    val engine = scriptEngineManager.engineByExtension("kts")
    engine.eval(input)
}
```