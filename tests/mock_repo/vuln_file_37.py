```kotlin
import java.util.*

class Animal(val name: String) {
    override fun toString(): String {
        return "Animal(name='$name')"
    }
}

class Dog(name: String) : Animal(name)

fun main() {
    val animalList: MutableList<Animal> = ArrayList()
    animalList.add(Dog("Bobby"))
    val firstAnimal = animalList[0]
    val dog = firstAnimal as Dog // Unchecked cast, can throw ClassCastException if firstAnimal is not a Dog
    println(dog)
}
```