```go
package main

import (
	"fmt"
	"unsafe"
)

func main() {
	b := make([]byte, 10)
	for i := 0; i < 20; i++ {
		*(*int32)(unsafe.Pointer(&b[0])) = int32(i)
	}
	fmt.Println(b)
}
```