```swift
import Foundation
import os.signpost

class BankAccount {
    private var balance: Int = 0
    private let lock = NSRecursiveLock()
    
    func deposit(_ amount: Int) {
        lock.lock()
        let currentBalance = balance
        Thread.sleep(forTimeInterval: 0.01) // Simulate processing time
        balance = currentBalance + amount
        lock.unlock()
    }
}

let account = BankAccount()

DispatchQueue.concurrentPerform(iterations: 1000) { _ in
    account.deposit(100)
}

print("Final balance: \(account.balance)")
```