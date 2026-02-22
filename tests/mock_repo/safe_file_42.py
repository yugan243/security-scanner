```swift
import Foundation

func concatenateStrings(_ strings: [String]) -> String {
    let result = strings.joined(separator: "")
    return result
}

let strings = ["a", "b", "c", "d", "e"]
print(concatenateStrings(strings))
```