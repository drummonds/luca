package main

import (
	"flag"
	"fmt"
	"log"

	"github.com/drummonds/luca/internal/parser"
)

// demoCommand implements the "demo" subcommand
func demoCommand() *Command {
	fs := flag.NewFlagSet("demo", flag.ExitOnError)

	return &Command{
		Name:    "demo",
		Usage:   "Input demo and show output",
		FlagSet: fs,
		Run: func(args []string, options *CommandOptions) {
			fs.Parse(args)

			input := `2024-03-20 generic "Grocery shopping"
    "assets:checking    -50.00"
    "expenses:food       50.00"

2024-03-21 txn "Coffee"
	cash 5.00 -> expenses:coffee
`

			if options.Verbose {
				fmt.Println("Parsing test input...")
			}

			doc, err := parser.Parse(input, "test.luca")
			if err != nil {
				log.Fatalf("Failed to parse: %v", err)
			}

			// Print the parsed entries
			lines := doc.ToLines()
			for _, line := range lines {
				fmt.Println(line)
			}
		},
	}
}
