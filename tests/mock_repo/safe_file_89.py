```swift
import Foundation

struct Buffer {
    private let data: Data
    
    init?(size: Int) {
        guard size > 0 else { return nil }
        self.data = Data(repeating: 0, count: size)
    }
}

func createBuffer() -> Buffer? {
    return Buffer(size: 1024)
}

func processData(_ buffer: Buffer?) {
    guard let buffer = buffer else { return }
    // Processing data...
}

if let buffer = createBuffer() {
    processData(buffer)
}
```