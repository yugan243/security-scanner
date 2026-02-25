```swift
import Foundation

enum NetworkError: Error {
    case invalidURL
    case networkRequestFailed(Error?)
}

func fetchDataFromServer(_ urlString: String, completion: @escaping (Result<Data, NetworkError>) -> Void) {
    if let url = URL(string: urlString) {
        let task = URLSession.shared.dataTask(with: url) { (data, response, error) in
            if let error = error {
                completion(.failure(.networkRequestFailed(error)))
            } else if let data = data {
                completion(.success(data))
            } else {
                completion(.failure(.networkRequestFailed(nil)))
            }
        }
        
        task.resume()
    } else {
        completion(.failure(.invalidURL))
    }
}

fetchDataFromServer("https://example.com") { result in
    switch result {
    case .success(let data):
        // do something with data
    case .failure(let error):
        print("Error: \(error)")
    }
}
```