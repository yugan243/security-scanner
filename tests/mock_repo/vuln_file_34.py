```swift
import Foundation

class VulnerableClass {
    var data: UnsafeMutablePointer<Int8>?
    
    init(size: Int) {
        self.data = UnsafeMutablePointer(calloc(size, 1))
    }
    
    deinit {
        free(self.data)
    }
    
    func writeData(_ newData: String) {
        let bytes = [UInt8](newData.utf8)
        bytes.withUnsafeBufferPointer { buffer in
            memcpy(self.data, buffer.baseAddress, buffer.count)
        }
    }
}

let instance = VulnerableClass(size: 10)
instance.writeData("This string is too long for the allocated memory")
```