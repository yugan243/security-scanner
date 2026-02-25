```go
package main

import (
	"fmt"
	"strings"
)

func main() {
	var strs []string
	for i := 0; i < 10000000; i++ {
		strs = append(strs, "a")
	}
	fmt.Println(strings.Join(strs, ""))
}
```