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
		{Name: "Number", Pattern: `[-+]?\d*\.?\d+`},
		{Name: "Arrow", Pattern: `->|→|⮕|🡒|⇒|⟶|➜|➝|➞|➡|⇨|⇾|⟹`}, // Extended arrow alternatives
		{Name: "Ident", Pattern: `[a-zA-Z][a-zA-Z0-9_:]*`},
		// {Name: "Punct", Pattern: `[-[!@#$%^&*()+_={}\|:;"'<,>.?/]|]`},
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
	Comments    []string      `parser:"@Comment*"`
	Date        string        `parser:"@Date"`
	Transaction *Transaction  `parser:"(@@"`
	Commodity   *Commodity    `parser:"| @@"`
	Generic     *GenericEntry `parser:"| @@)"`
}

func (e Entry) ToStringBuider(sb *strings.Builder) {
	for _, comment := range e.Comments {
		sb.WriteString(comment)
	}
	if e.Transaction != nil {
		e.Transaction.ToStringBuider(sb)
	}
	if e.Commodity != nil {
		e.Commodity.ToStringBuider(sb)
	}
	if e.Generic != nil {
		e.Generic.ToStringBuider(sb)
	}
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

func documentsEqual(a, b *Document) bool {
	if len(a.Entries) != len(b.Entries) {
		return false
	}

	for i, entry := range a.Entries {
		if !entriesEqual(entry, b.Entries[i]) {
			return false
		}
	}
	return true
}

// entriesEqual compares two Entries for equality
func entriesEqual(a, b *Entry) bool {
	if len(a.Comments) != len(b.Comments) {
		return false
	}
	for i, comment := range a.Comments {
		if comment != b.Comments[i] {
			return false
		}
	}
	if a.Date != b.Date {
		return false
	}

	// Compare Generic entries
	if a.Generic != nil && b.Generic != nil {
		return a.Generic.Equal(*b.Generic)
	}

	// Compare Transaction entries
	if a.Transaction != nil && b.Transaction != nil {
		return a.Transaction.Equal(b.Transaction)
	}

	// One is nil while the other isn't
	if (a.Generic == nil) != (b.Generic == nil) {
		return false
	}
	if (a.Transaction == nil) != (b.Transaction == nil) {
		return false
	}

	return true
}
