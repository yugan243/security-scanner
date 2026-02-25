```go
package main

import (
	"fmt"
	"reflect"
	"unsafe"
)

func main() {
	b := make([]byte, 200)
	for i := range b {
		b[i] = byte(i)
	}

	p1 := unsafe.Pointer(&b[0])

	// Use reflect package to get the size of the slice
	size := int(reflect.TypeOf(b).Size())

	// Check if the pointer offset is within the bounds of the slice
	if uintptr(208) >= uintptr(size) {
		fmt.Println("Pointer offset out of bounds")
		return
	}

	// Create a pointer to the 208th byte in the slice
	p2 := (*int16)(unsafe.Pointer(uintptr(p1) + 208))
	*p2 = 44

	fmt.Println("Value at index 208:", *p2)
}
```