package parser

import (
	"context"
	"fmt"
	"io"
	"os"
	"os/signal"
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
		{Name: "KnowledgeDate", Pattern: `\^\d{4}[-/]\d{2}[-/]\d{2}`},
		{Name: "String", Pattern: `"[^"]*"`}, // Keep simple string pattern without action
		{Name: "Number", Pattern: `[-+]?\d*\.?\d+`},
		{Name: "Arrow", Pattern: `->|→|⮕|🡒|⇒|⟶|➜|➝|➞|➡|⇨|⇾|⟹`}, // Extended arrow alternatives
		{Name: "Ident", Pattern: `[a-zA-Z][a-zA-Z0-9_:]*`},
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
	Comments      []string      `parser:"@Comment*"`
	Date          string        `parser:"@Date"`
	KnowledgeDate string        `parser:"@KnowledgeDate?"`
	Transaction   *Transaction  `parser:"(@@"`
	Commodity     *Commodity    `parser:"| @@"`
	Generic       *GenericEntry `parser:"| @@)"`
}

func (e Entry) ToStringBuider(sb *strings.Builder) {
	for _, comment := range e.Comments {
		sb.WriteString("; " + comment + "\n")
	}
	if e.Date != "" {
		sb.WriteString(e.Date)
	}
	if e.KnowledgeDate != "" {
		sb.WriteString(" ^" + e.KnowledgeDate)
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
		//^ from KnowledgeDate
		//; from Comment
		participle.Map(func(token lexer.Token) (lexer.Token, error) {
			switch {
			case token.Type == tokenLexer.Symbols()["String"] && len(token.Value) >= 2:
				token.Value = token.Value[1 : len(token.Value)-1]
			case token.Type == tokenLexer.Symbols()["KnowledgeDate"]:
				token.Value = token.Value[1:len(token.Value)]
			case token.Type == tokenLexer.Symbols()["Comment"]:
				token.Value = strings.TrimSpace(token.Value[1:len(token.Value)])
			}
			return token, nil
		}),
	)
}

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
	tokenEOF := indentLexer.Symbols()["EOF"]
	fmt.Println("TokenEOF", tokenEOF)

	// Create a context with cancellation for handling CTRL+C
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Set up signal handling for CTRL+C
	signalChan := make(chan os.Signal, 1)
	signal.Notify(signalChan, os.Interrupt)
	defer signal.Stop(signalChan)

	// Start a goroutine to handle the interrupt signal
	go func() {
		<-signalChan
		fmt.Println("\nReceived interrupt signal. Cancelling operation...")
		cancel()
	}()

	var token lexer.Token

	// Modified loop with context check
tokenLoop:
	for {
		select {
		case <-ctx.Done():
			fmt.Println("Operation cancelled")
			break tokenLoop
		default:
			token, err = tokens.Next()
			if err == io.EOF {
				break tokenLoop
			}
			if err != nil {
				return nil, err
			}
			if token.Type == tokenEOF {
				break tokenLoop
			}
			fmt.Printf("%+v: |%s|\n", token.Type, token.Value)
		}
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
