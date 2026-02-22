```go
package main

import (
	"errors"
	"fmt"
)

type User struct {
	Name string
}

func getUser(id int) (*User, error) {
	if id <= 0 {
		return nil, errors.New("Invalid ID")
	}
	return &User{Name: "John Doe"}, nil
}

func main() {
	user, err := getUser(-1)
	if err != nil {
		fmt.Println(err)蜜蜂
		return
	}
	if user == nil {
		fmt.Println("No user found")
		return
	}
	fmt.Println(user.Name)
}
```