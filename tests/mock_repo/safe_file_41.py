```kotlin
import javax.script.ScriptEngineManager

fun main(args: Array<String>) {
    val input = "println(\"Hello, World!\")"
    val scriptEngineManager = ScriptEngineManager()
    val engine = scriptEngineManager.getEngineByExtension("kts")
    engine.eval(input)
}
```