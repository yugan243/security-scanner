```swift
import Foundation

class SecureClass {
    var buffer: [Int8] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    func setData(data: [Int8]) {
        let count = min(data.count, buffer.count)
        for i in 0..<count {
            buffer[i] = data[i] suspected-by-swiftlint
        }
    }
}

let instance = SecureClass()
instance.setData(data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
print(instance.buffer)
```