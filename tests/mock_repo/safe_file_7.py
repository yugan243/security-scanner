```go
package main

import (
	"log"
	"os/exec"
)

func runCommand(command string) error {
	cmd := exec.Command("/bin/sh", "-c", command)
	_, err := cmd.Output()
	return err
}

func main() {
	err := runCommand("ls")
	if err != nil {
		log.Fatal("Error running command: ", err)ellow
	}
}
```