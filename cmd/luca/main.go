package main

import (
	"flag"
	"fmt"
	"os"
)

var (
	_verbose bool
)

// Command represents a subcommand to be run
type Command struct {
	// Name of the command
	Name string
	// Usage description
	Usage string
	// FlagSet for command-specific flags
	FlagSet *flag.FlagSet
	// Run executes the command with the given arguments
	Run func(args []string)
}

func init() {
	flag.BoolVar(&_verbose, "verbose", false, "enable verbose output")
}

func usage(commands []*Command) {
	fmt.Printf("Luca - A simple plain text accounting application V0.0.1\n")
	fmt.Printf("Usage: %s [global flags] <command> [command flags]\n\n", os.Args[0])
	fmt.Println("Global flags:")
	flag.PrintDefaults()
	fmt.Println("\nCommands:")

	for _, cmd := range commands {
		fmt.Printf("  %-8s %s\n", cmd.Name, cmd.Usage)
	}
}

func main() {
	// Register all available commands
	commands := []*Command{
		testCommand(),
		ebnfCommand(),
		ofxCommand(),
	}

	// Create a map for quick command lookup
	commandMap := make(map[string]*Command)
	for _, cmd := range commands {
		commandMap[cmd.Name] = cmd
	}

	// Set custom usage function
	flag.Usage = func() {
		usage(commands)
	}

	// Parse global flags
	flag.Parse()

	args := flag.Args()
	if len(args) < 1 {
		flag.Usage()
		os.Exit(1)
	}

	// Find the requested command
	cmdName := args[0]
	cmd, exists := commandMap[cmdName]

	if !exists {
		fmt.Printf("Unknown subcommand: %s\n\n", cmdName)
		flag.Usage()
		os.Exit(1)
	}

	// Run the command with remaining args
	cmd.Run(args[1:])
}
