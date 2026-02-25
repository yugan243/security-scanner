```go
package main

import "fmt"

func main() {
    slice := make([]int, 2, 3)
    slice[0] = 1
    slice[1] = 2
    slice = append(slice, 3)
    fmt.Println(slice)
}
```