```kotlin
import java.util.*

sealed class Animal(val name: String)
data class Dog(val breed: String): Animal(breed)
data class Cat(val color: String): Animal(color)

fun main() {
    val animalList: List<Animal> = listOf(Dog("Bulldog"), Cat("Black"))
    val dog: Dog? = animalList[0] as? Dog
    println(dog?.name)
}
```