```swift
import Foundation

class MyClass {
    var myBuffer: [UInt8] = Array(repeating: 0, count: 1024)
    
    func setData(_ data: [UInt8]) {
        let maxSize = 1024 // Define the maximum size of the buffer
        let dataCount = min(data.count, maxSize) // Make sure we don't exceed the buffer size
        myBuffer = Array(data[0..<dataCount]) // Assign only the valid data to the buffer
    }
}

let myInstance = MyClass()
myInstance.setData(Array(repeating: 0, count: 2048))
```