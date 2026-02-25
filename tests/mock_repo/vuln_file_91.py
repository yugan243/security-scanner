```swift
import Foundation

func evaluate(userInput: String) -> Any? {
    return eval(userInput)
}

let userInput = "4 * 5" // This is user input

if let result = evaluate(userInput: userInput) as? Int {
    print("Result: \(result)")
} else {
    print("Invalid input")
}
```