package parser

import (
	"context"
	"fmt"
	"io"
	"os"
	"os/signal"
	"strings"
	"time"

	"github.com/alecthomas/participle/v2"
	"github.com/alecthomas/participle/v2/lexer"
	"github.com/shopspring/decimal"
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
func TokenLexer() lexer.Definition {
	return lexer.Must(lexer.New(lexer.Rules{
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

func NewParser() (*participle.Parser[Document], error) {
	// Unfortunately, we can't directly parse into a Document with []JournalEntry
	// Since the Parse function has been rewritten to handle this properly,
	// this function is now deprecated but kept for API compatibility
	return nil, nil
}

// Parse takes a string input and returns a parsed Document
func ParseWithDebug(input string) (*Document, error) {
	// First pass: preprocess indentation and show tokens
	processedInput, err := PreprocessIndentation(input)
	if err != nil {
		return nil, err
	}

	// Display tokens for debugging
	tokenLexer := TokenLexer()
	tokens, err := tokenLexer.Lex("", strings.NewReader(processedInput))
	if err != nil {
		return nil, err
	}

	// Define token types
	tokenEOF := tokenLexer.Symbols()["EOF"]

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
			// fmt.Printf("%+v: |%s|\n", token.Type, token.Value)
		}
	}

	return Parse(input, "debug.luca")
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

// Parse parses the input string and returns a Document
func Parse(input string, filename string) (*Document, error) {
	// First pass: preprocess indentation and show tokens
	processedInput, err := PreprocessIndentation(input)
	if err != nil {
		return nil, err
	}

	doc := &Document{}

	err = ParseAndAddToDocument(processedInput, filename, doc)
	if err != nil {
		return nil, err
	}

	return doc, nil
}

type parseState int

const (
	matchEntryHeader parseState = iota
	matchDirective
	matchEOF
)

type (
	DirectiveNewFunc    func(*EntryHeader, string, *parserState)
	DirectiveParserFunc func(lexer.Token, lexer.Token, *parserState) (parseState, error)
	DirectiveAdderFunc  func(*Document, JournalEntry) error
)
type parserState struct {
	TokenLexer         lexer.Definition
	state              parseState
	directiveState     int
	tokenEOF           lexer.TokenType
	tokenIndent        lexer.TokenType
	tokenDedent        lexer.TokenType
	tokenNewline       lexer.TokenType
	tokenDate          lexer.TokenType
	tokenKnowledgeDate lexer.TokenType
	tokenString        lexer.TokenType
	tokenNumber        lexer.TokenType
	tokenArrow         lexer.TokenType
	tokenIdent         lexer.TokenType
	tokenWhitespace    lexer.TokenType
	tokenComment       lexer.TokenType
	directiveNewer     DirectiveNewFunc
	directiveParser    DirectiveParserFunc
	directiveAdder     DirectiveAdderFunc
	entry              JournalEntry
}

func NewParserState(tokenLexer lexer.Definition) *parserState {
	ps := &parserState{
		TokenLexer:         tokenLexer,
		state:              matchEntryHeader,
		tokenEOF:           tokenLexer.Symbols()["EOF"],
		tokenIndent:        tokenLexer.Symbols()["INDENT"],
		tokenDedent:        tokenLexer.Symbols()["DEDENT"],
		tokenNewline:       tokenLexer.Symbols()["Newline"],
		tokenDate:          tokenLexer.Symbols()["Date"],
		tokenKnowledgeDate: tokenLexer.Symbols()["KnowledgeDate"],
		tokenString:        tokenLexer.Symbols()["String"],
		tokenNumber:        tokenLexer.Symbols()["Number"],
		tokenArrow:         tokenLexer.Symbols()["Arrow"],
		tokenIdent:         tokenLexer.Symbols()["Ident"],
		tokenWhitespace:    tokenLexer.Symbols()["Whitespace"],
		tokenComment:       tokenLexer.Symbols()["Comment"],
	}
	return ps
}

func ParseAndAddToDocument(input string, filename string, doc *Document) error {
	var (
		token           lexer.Token
		nextToken       lexer.Token
		nextState       parseState
		directive       string
		thisEntryHeader *EntryHeader
	)
	tokenLexer := TokenLexer()
	ps := NewParserState(tokenLexer)
	// First pass: preprocess indentation and show tokens
	processedInput, err := PreprocessIndentation(input)
	if err != nil {
		return err
	}
	tokens, err := tokenLexer.Lex("", strings.NewReader(processedInput))
	if err != nil {
		return err
	}

	// Create a context with cancellation for handling CTRL+C if get stuck in an infinite loop
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

	thisEntryHeader = new(EntryHeader)
	thisEntryHeader.Filename = filename

	getNext := func() (lexer.Token, error) {
		for {
			nextToken, err = tokens.Next()
			if err != nil && err != io.EOF {
				return lexer.Token{}, err
			}
			if err == io.EOF {
				return lexer.Token{Type: ps.tokenEOF}, nil
			}
			// Skip whitespace
			if nextToken.Type != ps.tokenWhitespace {
				return nextToken, nil
			}
		}
	}
	nextToken, err = getNext()
	if err != nil && err != io.EOF {
		return err
	}

	// Modified loop with context check
tokenLoop:
	for {
		select {
		case <-ctx.Done():
			fmt.Println("Operation cancelled")
			break tokenLoop
		default:
			token = nextToken
			nextToken, err = getNext()
			if err != nil && err != io.EOF {
				return err
			}
			if err == io.EOF || token.Type == ps.tokenEOF {
				if ps.state == matchDirective {
					err = ps.directiveAdder(doc, ps.entry)
					if err != nil {
						return err
					}
					ps.entry = nil
				}
				break tokenLoop
			}
			// fmt.Printf("From Parser: %+v: |%s|\n", token.Type, token.Value)
			switch ps.state {
			case matchEntryHeader:
				nextState, directive, err = parseEntryHeader(token, nextToken, ps, thisEntryHeader)
				if err != nil {
					return err
				}
				if nextState == matchDirective {
					ps.directiveNewer = GetDirectiveNewer(directive)
					ps.directiveParser = GetDirectiveParser(directive)
					ps.directiveAdder = GetDirectiveAdder(directive)
					ps.directiveState = 0
					ps.directiveNewer(thisEntryHeader, directive, ps)
					thisEntryHeader = new(EntryHeader)
				}
			case matchDirective:
				nextState, err = ps.directiveParser(token, nextToken, ps)
				if err != nil {
					return err
				}
				if nextState != matchDirective {
					err = ps.directiveAdder(doc, ps.entry)
					if err != nil {
						return err
					}
					ps.entry = nil
				}
			}
			ps.state = nextState
		}
	}
	return nil
}

var (
	directiveNewers  = map[string]DirectiveNewFunc{}
	directiveParsers = map[string]DirectiveParserFunc{}
	directiveAdders  = map[string]DirectiveAdderFunc{}
)

func RegisterDirectiveNew(directive string, newFunc DirectiveNewFunc) {
	directiveNewers[directive] = newFunc
}

func RegisterDirectiveParser(directive string, parser DirectiveParserFunc) {
	directiveParsers[directive] = parser
}

func RegisterDirectiveAdder(directive string, adder DirectiveAdderFunc) {
	directiveAdders[directive] = adder
}

func GetDirectiveNewer(directive string) DirectiveNewFunc {
	return directiveNewers[directive]
}

func GetDirectiveParser(directive string) DirectiveParserFunc {
	return directiveParsers[directive]
}

func GetDirectiveAdder(directive string) DirectiveAdderFunc {
	return directiveAdders[directive]
}

// ParseFile parses a file and returns a Document
func ParseFile(filename string) (*Document, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to read file: %w", err)
	}
	return Parse(string(data), filename)
}

// ParseFiles parses multiple files and returns a merged Document
func ParseFiles(filenames ...string) (*Document, error) {
	doc := &Document{}

	for _, filename := range filenames {
		fileDoc, err := ParseFile(filename)
		if err != nil {
			return nil, fmt.Errorf("error parsing %s: %w", filename, err)
		}
		fmt.Printf("fileDoc: %+v\n", fileDoc)
		// doc.Entries = append(doc.Entries, fileDoc.Entries...)
	}

	return doc, nil
}

// Helper function to parse date strings into time.Time
func ParseDate(dateStr string) time.Time {
	t, _ := time.Parse("2006-01-02", dateStr)
	return t
}

func ParseNumber(numberStr string) (decimal.Decimal, error) {
	n, err := decimal.NewFromString(numberStr)
	return n, err
}

func DeQuote(s string) string {
	if len(s) >= 2 {
		return s[1 : len(s)-1]
	}
	return s
}
