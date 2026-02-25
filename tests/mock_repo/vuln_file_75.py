```swift
import Foundation

func getUserInput() -> String {
    let args = CommandLine.arguments
    guard args.count > 1 else {
        fatalError("No input provided")
    }
    return args[1]
}

func processInput(input: String) -> String {
    var result = ""
    for i in 0..<input.count {
        result += input[input.index(input.startIndex, offsetBy: i)]
    }
    return result
}

let userInput = getUserInput()
let processedInput = processInput(input: userInput)
print(processedInput)
```