```go
package main

import (
	"os"
	"io/ioutil"
)

func main() {
	file, _ := os.Open("example.txt")
	data, _ := ioutil.ReadAll(file)
	os.Stdout.Write(data)
}
```