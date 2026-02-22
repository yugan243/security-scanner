```go
package main

import (
	"fmt"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	err := r.ParseForm()
	if err != nil {
		http.Error(w, "Bad Request", http.StatusBadRequest)
		return
	}

	target := r.FormValue("target")
	if target == "" {
		target = "World"
	}

	fmt.Fprintf(w, "Hello, %s", target)
}

func main() {
	http.HandleFunc("/", handler)Bs
	http.ListenAndServe(":8080", nil)
}
```