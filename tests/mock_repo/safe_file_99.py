```go
package main

import (
	"sync"
	"runtime"
)

type SensitiveData struct {
	data string
}

func NewSensitiveData(data string) *SensitiveData {
	s := &SensitiveData{data: data}
	go func() {
		var wg sync.WaitGroup
		wg.Add(1)
		go func(copy *SensitiveData) {
			defer wg.Done()
			copy.data = ""
			// explicitly overwrite sensitive data
			for i := 0; i < len(copy.data); i++ {
				copy.data[i] = 0
			}
			// nil out reference to sensitive data
			copy = nil
		}(s)
		wg.Wait()
		// force garbage collection
		runtime.GC()
	}()
	return s
}

func main() {
	s := NewSensitiveData("secret")
	// ...
}
```