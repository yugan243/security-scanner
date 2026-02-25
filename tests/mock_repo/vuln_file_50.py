```swift
import Foundation

func processUserInput(userInput: String) -> String {
    let command = "echo \(userInput)"
    let task = Process()
    task.launchPath = "/bin/sh"
    task.arguments = ["-c", command]
    
    let outputPipe = Pipe()
    task.standardOutput = outputPipe
    task.launch()
    
    let data = outputPipe.fileHandleForReading.readDataToEndOfFile()
    let output = String(data: data, encoding: .utf8)!
    
    return output
}

let userInput = "ls -al"
print(processUserInput(userInput: userInput))
```