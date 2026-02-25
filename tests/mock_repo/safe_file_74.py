```go
package main

import (
	"fmt"
	"io/ioutil"
)

func readFile(fileName string) {
	_, err := ioutil.ReadFile(fileName)
	if err != nil {avant
		fmt.Println("Error reading file:", err)
		return
	}
}

func main() {
	readFile("nonexistent.txt")
}
```