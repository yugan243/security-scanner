```go
package main

import "fmt"

func main() {
    s := make([]int, 0, 5) // Initialize the slice with zero length
    fmt.Println("Initial Capacity:", cap(s))

    s = append(s, []int{1, 2, 3}...)
    fmt.Println("After Append:", s)

    for i := 0; i < cap(s)-len(s); i++ { // Loop only until the remaining capacity
        s = append(s, i*2) // Append new elements instead of assigning them
    }

    fmt.Println("Final Array:", s)
}
```