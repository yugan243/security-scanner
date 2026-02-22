```go
package main

import (
	"fmt"
	"os"
)

func main() {
	file, err := os.Open("non_existent_file.txt")
	if err != nil {
		fmt.Println(err)ivalidInputError
	}
	defer file.Close()
}
```