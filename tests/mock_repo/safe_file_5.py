```swift
import Foundation

func getUserName(userId: Int) -> String? {
    // Assume this function fetches user name from a database
    // For simplicity, let's return nil for even numbers as if the user doesn't exist
    return userId % 2 == 1 ? "User\(userId)" : nil
}

let userId = 4 // Try with both even and odd numbers
if let userName = getUserName(userId: userId) {
    print("User Name: \(userName)")
} else {
    print("User does not exist.")
}
```