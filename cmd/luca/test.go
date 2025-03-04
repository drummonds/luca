package main

import (
	"flag"
	"fmt"
	"log"

	"github.com/drummonds/luca/internal/parser"
)

// testCommand implements the "test" subcommand
func testCommand() *Command {
	fs := flag.NewFlagSet("test", flag.ExitOnError)

	return &Command{
		Name:    "test",
		Usage:   "Run parser tests on sample input",
		FlagSet: fs,
		Run: func(args []string) {
			fs.Parse(args)

			input := `2024-03-20 generic "Grocery shopping"
    "assets:checking    -50.00"
    "expenses:food       50.00"

2024-03-21 txn "Coffee"
	cash 5.00 -> expenses:coffee
`

			if _verbose {
				fmt.Println("Parsing test input...")
			}

			doc, err := parser.Parse(input)
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
