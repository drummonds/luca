package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"

	"github.com/drummonds/luca/internal/parser"
)

// ofxCommand implements the "ofx" subcommand for importing OFX files
func ofxCommand() *Command {
	fs := flag.NewFlagSet("ofx", flag.ExitOnError)

	var (
		outputFile  string
		accountName string
	)

	fs.StringVar(&outputFile, "output", "", "Output file path (if not specified, prints to stdout)")
	fs.StringVar(&accountName, "account", "assets:checking", "Default account name to use for transactions")

	return &Command{
		Name:    "ofx",
		Usage:   "Import an OFX/QFX file and add to Luca Ledger",
		FlagSet: fs,
		Run: func(args []string) {
			fs.Parse(args)

			// Check if we have input files
			files := fs.Args()
			if len(files) == 0 {
				fmt.Println("Error: No input files specified")
				fmt.Println("Usage: luca ofx [options] <file1.ofx> [file2.ofx...]")
				os.Exit(1)
			}

			// Process each file
			doc := &parser.Document{}

			for _, filename := range files {
				if _verbose {
					fmt.Printf("Processing %s...\n", filename)
				}

				// // Import the OFX file
				// err := importOFXFile(filename, accountName, ledger)
				// if err != nil {
				// 	log.Fatalf("Error importing %s: %v", filename, err)
				// }

				// // Add the transactions to our document
				// doc.Entries = append(doc.Entries, transactions...)

				// if _verbose {
				// 	fmt.Printf("Imported %d transactions from %s\n", len(transactions), filename)
				// }
			}

			// Convert to string representation
			output := strings.Join(doc.ToLines(), "\n")

			// Save or print
			if outputFile != "" {
				err := ioutil.WriteFile(outputFile, []byte(output), 0644)
				if err != nil {
					log.Fatalf("Error writing to %s: %v", outputFile, err)
				}
				if _verbose {
					fmt.Printf("Output written to %s\n", outputFile)
				}
			} else {
				fmt.Println(output)
			}
		},
	}
}

// // importOFXFile reads and parses an OFX file and returns Luca entries
// func importOFXFile(filename, defaultAccount string) ([]parser.Entry, error) {
// 	// Read the file
// 	file, err := os.Open(filename)
// 	if err != nil {
// 		return nil, fmt.Errorf("could not open file: %w", err)
// 	}
// 	defer file.Close()

// 	// Parse the OFX data
// 	response, err := ofxgo.ParseResponse(file)
// 	if err != nil {
// 		return nil, fmt.Errorf("error parsing OFX: %w", err)
// 	}

// 	// Convert to Luca entries
// 	var entries []parser.Entry

// 	// Process bank statement responses
// 	for _, stmt := range response.Bank {
// 		// Process transactions in the statement
// 		for _, txn := range stmt.BankTranList.Transactions {
// 			// Create a new entry
// 			entry := parser.Entry{
// 				Type:  "generic",
// 				Date:  txn.DtPosted.Time,
// 				Payee: txn.Name.String(),
// 				PostingStrings: []string{
// 					fmt.Sprintf("%s %.2f", defaultAccount, -txn.TrnAmt.Float64()),
// 					fmt.Sprintf("expenses:unknown %.2f", txn.TrnAmt.Float64()),
// 				},
// 			}

// 			entries = append(entries, entry)
// 		}
// 	}

// 	// Process credit card statement responses
// 	for _, stmt := range response.CreditCard {
// 		// Process transactions in the statement
// 		for _, txn := range stmt.BankTranList.Transactions {
// 			// Create a new entry
// 			entry := parser.Entry{
// 				Type:  "generic",
// 				Date:  txn.DtPosted.Time,
// 				Payee: txn.Name.String(),
// 				PostingStrings: []string{
// 					fmt.Sprintf("%s %.2f", defaultAccount, -txn.TrnAmt.Float64()),
// 					fmt.Sprintf("expenses:unknown %.2f", txn.TrnAmt.Float64()),
// 				},
// 			}

// 			entries = append(entries, entry)
// 		}
// 	}

// 	return entries, nil
// }
