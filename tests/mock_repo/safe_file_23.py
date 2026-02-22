```swift
import Foundation

struct Buffer {
    var data: [UInt8] = []
    let size: Int
    
    mutating func writeToBuffer(_ data: [UInt8]) {
        let availableSpace = size - data.count
        if availableSpace >= 0 {
            self.data.append(contentsOf: data[...availableSpace-1])
        } else {
            print("Error: Not enough space in buffer.")
        }
    }
}

var myBuffer = Buffer(size: 10)
let dataToWrite = Array(repeating: 0xFF, count: 20)
myBuffer.writeToBuffer(dataToWrite)
print("Buffer data: \(myBuffer.data)")
```