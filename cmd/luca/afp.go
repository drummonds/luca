package main

import (
	"flag"
	"fmt"
	"log"

	"github.com/drummonds/luca"
	"github.com/drummonds/luca/internal/parser"
)

const AFP1 = `
2025-01-01 commodty GBP
2025-01-01 open equity:input
2025-01-01 open assets:cash

2024-03-21 txn "Investment"
	equity:input 25.00 -> assets:cash
`

// afpCommand implements the "afp" subcommand demoing account for programmers examples
func afpCommand() *Command {
	fs := flag.NewFlagSet("afp", flag.ExitOnError)

	return &Command{
		Name:    "afp",
		Usage:   "Accounting for programmers examples",
		FlagSet: fs,
		Run: func(args []string, options *CommandOptions) {
			var input string
			var name string
			if err := fs.Parse(args); err != nil {
				log.Fatal(err)
			}

			args = fs.Args()
			if len(args) != 1 {
				log.Fatalf("Expected 1 argument number of example, got %d", len(args))
			}

			afp := args[0]
			if afp == "1" {
				input = AFP1
				name = "afp1.luca"
			} else {
				log.Fatalf("Unknown example number: %s", afp)
				return
			}

			// Read the input
			// Write the balance sheet
			// the summary in mermaid
			//save to a file
			// check read the file and save again and unchanged.

			if options.Verbose {
				fmt.Println("Parsing test input...")
			}

			doc, err := parser.Parse(input, name)
			if err != nil {
				log.Fatalf("Failed to parse: %v", err)
			}

			ledger, err := luca.NewLedgerFrom(name, true)
			if err != nil {
				log.Fatalf("Failed to create ledger: %v", err)
			}
			ledger.AddDocument(doc, name, true)
			// Write the balance sheet
		},
	}
}
