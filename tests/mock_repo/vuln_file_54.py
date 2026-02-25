```swift
import Foundation

class User {
    var name: String?
    
    func greet() {
        print("Hello, \(name!)")
    }
}

let user = User()
user.greet()
```