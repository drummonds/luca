package main

import (
	"flag"
	"fmt"

	"github.com/alecthomas/participle/v2"
	"github.com/drummonds/luca/internal/parser"
)

// ebnfCommand implements the "ebnf" subcommand
func ebnfCommand() *Command {
	fs := flag.NewFlagSet("ebnf", flag.ExitOnError)

	return &Command{
		Name:    "ebnf",
		Usage:   "Generate EBNF grammar for the parser",
		FlagSet: fs,
		Run: func(args []string, options *CommandOptions) {
			fs.Parse(args)

			if options.Verbose {
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
		},
	}
}
