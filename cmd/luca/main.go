package main

import (
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/alecthomas/participle/v2"
	"github.com/drummonds/luca/internal/parser"
)

var (
	_verbose bool
)

func init() {
	flag.BoolVar(&_verbose, "verbose", false, "enable verbose output")
}

func usage() {
	fmt.Printf("Usage: %s [global flags] <command> [command flags]\n\n", os.Args[0])
	fmt.Println("Global flags:")
	flag.PrintDefaults()
	fmt.Println("\nCommands:")
	fmt.Println("  test    Run parser tests on sample input")
	fmt.Println("  ebnf    Generate EBNF grammar for the parser")
}

func test(args []string) {
	testCmd := flag.NewFlagSet("test", flag.ExitOnError)
	testCmd.Parse(args)

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
}

func ebnf(args []string) {
	ebnfCmd := flag.NewFlagSet("ebnf", flag.ExitOnError)
	ebnfCmd.Parse(args)

	if _verbose {
		fmt.Println("Generating EBNF grammar...")
	}

	// Create a new parser with lexer
	parser := participle.MustBuild[parser.Document](
		participle.Lexer(parser.TokenLexer()),
		participle.Elide("Whitespace", "Comment"),
		participle.UseLookahead(2),
	)

	// Generate and print the EBNF
	fmt.Println("\nGrammar:")
	fmt.Println(parser.String())
}

func main() {
	flag.Usage = usage
	flag.Parse()

	args := flag.Args()
	if len(args) < 1 {
		flag.Usage()
		os.Exit(1)
	}

	switch args[0] {
	case "test":
		test(args[1:])
	case "ebnf":
		ebnf(args[1:])
	default:
		fmt.Printf("Unknown subcommand: %s\n\n", args[0])
		flag.Usage()
		os.Exit(1)
	}
}
