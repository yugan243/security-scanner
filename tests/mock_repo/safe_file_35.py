```swift
import Foundation

class UnsafeClass {
    private var unsafePointer: UnsafeMutableRawPointer?
    
    init() {
        let size = 1024 * 1024 * 1024 // One gigabyte
        unsafePointer = UnsafeMutableRawPointer.allocate(byteCount: size, alignment: 1)
    }
    
    deinit {
        guard let pointer = unsafePointer else { return }
        pointer.deallocate(capacity: 1024 * 1024 * 1024)
        unsafePointer = nil
    }
}

var instance: UnsafeClass? = UnsafeClass()
instance = nil // Now this will properly deallocate the memory
```