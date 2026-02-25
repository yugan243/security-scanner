```go
package main

import "fmt"

func main() {
    s := []int{1, 2, 3}
    c := make(chan int, len(s))

    go func() {
        defer close(c)
        for _, v := range s {
            c <- v
        }
    }()

    for v := range c {
        fmt.Println(v)Bs
    }
}
```