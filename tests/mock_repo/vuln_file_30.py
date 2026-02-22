```swift
import Foundation

func vulnerableFunction1(input: String) -> String {
    var buffer = Array<UInt8>(repeating: 0, count: 1024)
    let inputData = input.utf8
    let length = min(buffer.count, inputData.count)
    buffer.withUnsafeMutableBufferPointer { pointer in
        pointer.baseAddress?.copyBytes(from: inputData, count: length)
    }
    return String(decoding: Data(bytes: &buffer, count: buffer.count), as: UTF8.self)
}

func vulnerableFunction2(input: String) -> String {
    var buffer = Array<UInt8>(repeating: 0, count: 1024)
    let inputData = input.utf8
    let length = min(buffer.count, inputData.count)
    buffer.withUnsafeMutableBufferPointer { pointer in
        pointer.baseAddress?.copyBytes(from: inputData, count: length)
    }
    return String(decoding: Data(bytes: &buffer, count: buffer.count), as: UTF8.self)
}

let userInput = "This is a long string that will cause a buffer overflow"
print(vulnerableFunction1(input: userInput))
print(vulnerableFunction2(input: userInput))
```