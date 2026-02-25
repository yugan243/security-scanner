```swift
import Foundation
import UIKit

class ViewController: UIViewController {
  @IBOutlet weak var inputField: UITextField
  @IBAction func submitButtonPressed(_ sender: Any) {
    let userInput = inputField.text
    let urlString = "https://example.com/search?q=\(userInput)"
    if let url = URL(string: urlString) {
      if let urlRequest = URLRequest(url: url) {
        let task = URLSession.shared.dataTask(with: urlRequest) { (data, response, error) in
          // handle response
        }
        task.resume()
      }
    }
  }
}
```