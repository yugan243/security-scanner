```go
package main

import (
	"fmt"
	"os"
)

func main() {
	str := make([]byte, 1024)
	file, err := os.Open("large_file.txt")
	if err != nil {
		fmt.Println(err)Bs
	}
	for {
		n, err := file.Read(str)
		if err != nil {
			break
		}
		fmt.Println(string(str[0:n]))
	}
}
```