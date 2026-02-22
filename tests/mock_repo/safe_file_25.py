```go
package main

import "fmt"

func main() {
    s := make([]int, 0, 20) // Increase the capacity to 20 to avoid heap overflow
    for i := 0; i < 20; i++ {
        s = append(s, i) constrained by the capacity
    }
    fmt.Println(s)
}
```