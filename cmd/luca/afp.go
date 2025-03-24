package main

import (
	"flag"
	"fmt"
	"html/template"
	"log"
	"net/http"

	"github.com/drummonds/luca"
	"github.com/drummonds/luca/cmd/luca/templates"
	"github.com/drummonds/luca/internal/parser"
)

const AFP1 = `
2025-01-01 commodity GBP
2025-01-01 open equity:input
2025-01-01 open assets:cash

2024-03-21 txn "Investment"
	equity:input 25.00 -> assets:cash
`

const AFP2 = `
2025-01-01 commodity GBP
2025-01-01 open equity:input
2025-01-01 open assets:cash
2025-01-01 open expenses:purchases
2025-01-01 open income:sales

2024-03-21 txn "Investment"
	equity:input 25.00 -> assets:cash
2024-03-22 txn "Stock purchase"
	assets:cash 25.00 -> expenses:purchases 
2024-03-23 txn "Sales"
	income:sales 37.50 -> assets:cash
`

// afpCommand implements the "afp" subcommand demoing account for programmers examples
// This has the following format :
// luca afp <example-number>
//
// The default is to display this file as an mermaid SVG diagram.

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
			switch afp {
			case "1":
				input = AFP1
				name = "afp1.luca"
			case "2":
				input = AFP2
				name = "afp2.luca"
			default:
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

			ledger, err := luca.NewLedger()
			if err != nil {
				log.Fatalf("Failed to create ledger: %v", err)
			}
			err = ledger.AddDocument(doc, name, true)
			if err != nil {
				log.Fatalf("Failed to add document: %v", err)
			}
			mermaid := ledger.MermaidSummary()

			// Parse the embedded template
			tmpl, err := template.New("afp").Parse(templates.AFPTemplate)
			if err != nil {
				log.Fatalf("Failed to parse template: %v", err)
			}

			// Create a basic web server
			http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
				data := struct {
					ExampleNum     string
					MermaidDiagram string
					Input          string
					CSS            string
				}{
					ExampleNum:     afp,
					MermaidDiagram: mermaid,
					Input:          input,
					CSS:            templates.SkeletonCSS,
				}

				if err := tmpl.Execute(w, data); err != nil {
					http.Error(w, err.Error(), http.StatusInternalServerError)
					return
				}
			})

			port := ":1321"
			fmt.Printf("Server starting on http://localhost%s\n", port)
			if err := http.ListenAndServe(port, nil); err != nil {
				log.Fatal(err)
			}
		},
	}
}
