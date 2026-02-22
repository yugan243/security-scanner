```swift
import Foundation

func vulnerableFunction(_ input: String) -> String {
    var buffer = Array<UInt8>(repeating: 0, count: 1024)
    let data = input.utf8
    buffer.withUnsafeMutableBufferPointer {
        let bytesWritten = data.withUnsafeBytes {
            bufferPointer in
            bufferPointer.baseAddress?.copyBytes(from: $0, count: data.count)
        }
        return String(decoding: buffer, as: UTF8.self)
    }
}

let input = "Some long string that will cause a buffer overflow"
print(vulnerableFunction(input))
```