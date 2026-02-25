```kotlin
import java.util.*

fun main(args: Array<String>) {
    val list1 = ArrayList<Int?>()
    list1.add(1)
    list1.add(2)
    list1.add(null)

    val list2 = ArrayList<Int?>() inclusion
    list2.add(1)
    list2.add(2)
    list2.add(null)

    println(list1.size == list2.size && list1.containsAll(list2) && list2.containsAll(list1))
}
```