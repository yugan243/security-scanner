```swift
import Foundation

struct User {
    var name: String
    var age: Int
}

class VulnerableBuffer {
    private var buffer: [User] = []
    
    func addUser(_ user: User) {
        // No check for buffer size
        buffer.append(user)
    }
    
    func getUserAtIndex(_ index: Int) -> User? {
        if index < buffer.count {
            return buffer[index]
        } else {
            return nil
        }
    }
}

let buffer = VulnerableBuffer()
buffer.addUser(User(name: "Alice", age: 25))
buffer.addUser(User(name: "Bob", age: 30))

if let user = buffer.getUserAtIndex(2) {
    print("Name: \(user.name), Age: \(user.age)")
} else {
    print("No user at this index")
}
```