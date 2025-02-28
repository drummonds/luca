package parser

import (
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/alecthomas/participle/v2"
	"github.com/alecthomas/participle/v2/lexer"
)

const (
	TabWidth = 4 // Number of spaces a tab represents
)

// calculateIndent counts indentation with tabs as TabWidth spaces
func calculateIndent(s string) int {
	indent := 0
	for _, ch := range s {
		switch ch {
		case ' ':
			indent++
		case '\t':
			indent += TabWidth
		}
	}
	return indent
}

// First pass: handle indentation
var indentLexer = lexer.Must(lexer.New(lexer.Rules{
	"Root": {
		{Name: "NEWLINE", Pattern: `\n`},
		{Name: "INDENT", Pattern: `^[ \t]+`},
		{Name: "TEXT", Pattern: `[^\n]+`},
		{Name: "WS", Pattern: `[ \t]+`},
	},
}))

// Second pass: actual token lexer
var tokenLexer = lexer.Must(lexer.New(lexer.Rules{
	"Root": {
		{Name: "INDENT", Pattern: `INDENT`}, // For the synthetic INDENT token
		{Name: "DEDENT", Pattern: `DEDENT`}, // For the synthetic DEDENT token
		{Name: "Newline", Pattern: `\n+`},   // Handle one or more newlines
		{Name: "Date", Pattern: `\d{4}[-/]\d{2}[-/]\d{2}`},
		{Name: "String", Pattern: `"[^"]*"`}, // Keep simple string pattern without action
		// {Name: "StringContent", Pattern: `(?:[^"\\]|\\.)*`},
		{Name: "Number", Pattern: `[-+]?\d*\.?\d+`},
		{Name: "Ident", Pattern: `[a-zA-Z][a-zA-Z0-9_:]*`},
		{Name: "Account", Pattern: `[a-zA-Z][a-zA-Z0-9_:]*:[a-zA-Z][a-zA-Z0-9_:]*`},
		{Name: "Punct", Pattern: `[-[!@#$%^&*()+_={}\|:;"'<,>.?/]|]`},
		{Name: "Whitespace", Pattern: `[ \t]+`, Action: nil},
		{Name: "Comment", Pattern: `;[^\n]*`, Action: nil},
	},
}))

// TokenLexer returns the lexer used for tokenizing input
func TokenLexer() lexer.Definition {
	return tokenLexer
}

// PreprocessIndentation converts raw text into a format with explicit INDENT/DEDENT tokens
func PreprocessIndentation(input string) (string, error) {
	tokens, err := indentLexer.Lex("", strings.NewReader(input))
	if err != nil {
		return "", err
	}

	// Get token types from lexer
	tokenNewline := indentLexer.Symbols()["NEWLINE"]
	tokenIndent := indentLexer.Symbols()["INDENT"]
	tokenText := indentLexer.Symbols()["TEXT"]
	tokenEOF := indentLexer.Symbols()["EOF"]

	var result strings.Builder
	stack := []int{0} // indentation stack
	eofHandler := func() (string, error) {
		for i := len(stack) - 1; i > 0; i-- {
			result.WriteString("\nDEDENT")
		}
		return result.String(), nil
	}
	currentIndent := 0
	lineCount := 1

	for {
		token, err := tokens.Next()
		if err == io.EOF {
			return eofHandler()
		}
		if err != nil {
			return "", fmt.Errorf("at line %d token error %+v", lineCount, err)
		}

		switch token.Type {
		case tokenEOF:
			return eofHandler()
		case tokenNewline:
			result.WriteString("\n")
			currentIndent = 0
			lineCount++
		case tokenIndent:
			currentIndent = calculateIndent(token.Value)
		case tokenText:
			if currentIndent > stack[len(stack)-1] {
				result.WriteString("INDENT ")
				stack = append(stack, currentIndent)
			} else {
				for currentIndent < stack[len(stack)-1] {
					result.WriteString("DEDENT ")
					stack = stack[:len(stack)-1]
				}
				if currentIndent != stack[len(stack)-1] {
					return "", fmt.Errorf("indentation mismatch at line %d", lineCount)
				}
			}
			result.WriteString(token.Value)
		}
	}
}

// Entry in journal
type Entry struct {
	Date        string        `parser:"@Date"`
	Generic     *GenericEntry `parser:"@@?"`
	Transaction *Transaction  //`parser:"| @@?)"`
}

// A generic format to illustrate the meta structure of an entry
type GenericEntry struct {
	Directive     string         `parser:" @'generic' "`
	Description   string         `parser:" (@String)?"`
	SubDirectives []SubDirective `parser:"('INDENT' @@+ 'DEDENT')?"`
}

// An accounting transaction
type Transaction struct {
	Directive   string     `parser:"@( 'txn' | '*' )"`
	Description string     `parser:"@String?"`
	Movements   []Movement `parser:"('INDENT' @@+ 'DEDENT')?"`
}

// Posting represents an account posting
type SubDirective struct {
	Text string `parser:"@String"`
}

// Posting represents an account posting
type Movement struct {
	From   string `parser:"@Account"`
	Amount string `parser:"('->' | '→' | '⮕' | '🡒')@Number"`
	To     string `parser:"@Account"`
}

// Document represents the entire file
type Document struct {
	Entries []*Entry `parser:"@@*"`
}

func NewParser() (*participle.Parser[Document], error) {
	return participle.Build[Document](
		participle.Lexer(tokenLexer),
		participle.Elide("Comment", "Whitespace", "Newline"),
		// Add a transformer to remove quotes from strings
		participle.Map(func(token lexer.Token) (lexer.Token, error) {
			if token.Type == tokenLexer.Symbols()["String"] && len(token.Value) >= 2 {
				token.Value = token.Value[1 : len(token.Value)-1]
			}
			return token, nil
		}),
	)
}

func NewParserWithDebug() (*participle.Parser[Document], error) {
	return participle.MustBuild[Document](
		participle.Lexer(tokenLexer),
		participle.Elide("Comment", "Whitespace", "Newline"),
		participle.UseLookahead(2),
	), nil
} // Add this line for detailed trace output

// Parse takes a string input and returns a parsed Document
func Parse(input string) (*Document, error) {
	// First pass: handle indentation
	processedInput, err := PreprocessIndentation(input)
	if err != nil {
		return nil, err
	}

	// Second pass: parse the processed input
	parser, err := NewParser()
	if err != nil {
		return nil, err
	}

	return parser.ParseString("", processedInput)
}

// Parse takes a string input and returns a parsed Document
func ParseWithDebug(input string) (*Document, error) {
	// First pass: handle indentation
	processedInput, err := PreprocessIndentation(input)
	if err != nil {
		return nil, err
	}

	tokens, err := tokenLexer.Lex("", strings.NewReader(processedInput))
	if err != nil {
		return nil, err
	}
	fmt.Println("Tokenenised")
	tokenEOF := indentLexer.Symbols()["EOF"] // || token.Type == tokenEOF
	fmt.Println("TokenEOF", tokenEOF)
	var (
		token lexer.Token
	)
	for {
		token, err = tokens.Next()
		if err == io.EOF {
			break
		}
		if token.Type == tokenEOF {
			break
		}
		fmt.Printf("%+v: |%s|\n", token.Type, token.Value)
	}

	// Second pass: parse the processed input
	parser, err := NewParser()
	if err != nil {
		return nil, err
	}

	return parser.ParseString("", processedInput,
		participle.Trace(os.Stdout),
	)
}

// SumIntsOrFloats sums the values of map m. It supports both int64 and float64
// as types for map values.
func ArrayEqual[T comparable](A, B []T) bool {
	if len(A) != len(B) {
		return false
	}
	for i := range A {
		if A[i] != B[i] {
			return false
		}
	}
	return true
}

func (a SubDirective) Equal(b SubDirective) bool {
	return a.Text == b.Text
}

func (a Movement) Equal(b Movement) bool {
	if a.To != b.To {
		return false
	}
	if a.From != b.From {
		return false
	}
	if a.Amount != b.Amount {
		return false
	}
	return true
}
