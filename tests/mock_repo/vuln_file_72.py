```go
package main

import (
	"fmt"
	"os"
)

func readFile(fileName string) {
	file, err := os.Open(fileName)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	buffer := make([]byte, 1024)
	for {
		n, err := file.Read(buffer)
		if n > 0 {
			fmt.Println(string(buffer[:n]))
		}
		if err != nil {
			break
		}
	}
}

func main() {
	readFile("/path/to/your/file")
}
```