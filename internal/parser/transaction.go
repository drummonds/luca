package parser

import (
	"fmt"
	"strings"

	"github.com/alecthomas/participle/v2/lexer"
	"github.com/shopspring/decimal"
)

// Transaction represents a financial transaction with postings
type Transaction struct {
	EntryHeader

	// Directive is "txn" or "generic"
	Directive   string      `parser:"@('txn' | '*' | 'transaction')"`
	Description string      `parser:"@String?"`
	Comment     string      `parser:"@Comment?"`
	Movements   []*Movement `parser:"( Indent @@+ 'DEDENT')?"`
}

// Posting represents an account posting
type Movement struct {
	From   string          `parser:"@Ident"`
	Amount decimal.Decimal `parser:"@Number"`
	Arrow  string          `parser:"@Arrow"` // Store arrow type so can tround trip
	To     string          `parser:"@Ident"`
}

// transactionsEqual compares two Transactions for equality
func (a *Transaction) Equal(b *Transaction) bool {
	if a.Directive != b.Directive {
		return false
	}
	return ArrayEqual(a.Movements, b.Movements)
}

func (a Movement) Equal(b Movement) bool {
	if a.To != b.To {
		return false
	}
	if a.From != b.From {
		return false
	}
	if !a.Amount.Equal(b.Amount) {
		return false
	}
	if a.Arrow != b.Arrow {
		return false
	}
	return true
}

// ToStringBuilder writes the transaction to a string builder
func (t *Transaction) ToStringBuilder(sb *strings.Builder) {
	// Write header fields
	t.EntryHeader.ToStringBuilder(sb)

	// Add directive and payee
	sb.WriteString(" ")
	sb.WriteString(t.Directive)
	sb.WriteString(" ")
	sb.WriteString(`"` + t.Description + `"`)
	sb.WriteString("\n")

	// Add movements if any
	for _, movement := range t.Movements {
		movement.ToStringBuilder(sb)
	}
}

func (m Movement) ToStringBuilder(sb *strings.Builder) {
	sb.WriteString("\t")
	sb.WriteString(m.From + " ")
	sb.WriteString(m.Amount.String() + " ")
	sb.WriteString(m.Arrow + " ")
	sb.WriteString(m.To)
	sb.WriteString("\n")
}

// GetDirective returns the transaction directive type
func (t *Transaction) GetDirective() string {
	return t.Directive
}

type transactionDirectiveState int

const (
	transactionDirectiveStateStart transactionDirectiveState = iota
	transactionDirectiveComment
	transactionDirectiveIndentOrNew
	transactionDirectiveExpectIndent
	transactionDirectiveSubDirectiveFrom
	transactionDirectiveSubDirectiveAmount
	transactionDirectiveSubDirectiveArrow
	transactionDirectiveSubDirectiveTo
	transactionDirectiveSubDirectivesEnd
)

// Transaction = ("txn" | "*") <string>? <comment>? ("INDENT" Movement+ "DEDENT")? .
// Movement = <ident> <number> <arrow> <ident> .
func ParseTransactionDirective(token lexer.Token, nextToken lexer.Token, ps *parserState) (parseState, error) {
	if ps.entry == nil {
		return matchEntryHeader, fmt.Errorf("entry must be initialised before parsing starts")
	}
	transaction := ps.entry.(*Transaction)
	switch transactionDirectiveState(ps.directiveState) {
	case transactionDirectiveStateStart:
		switch token.Type {
		case ps.tokenString:
			transaction.Description = DeQuote(token.Value)
			ps.directiveState = int(transactionDirectiveComment)
			return matchDirective, nil
		case ps.tokenString, ps.tokenNewline: // allow none
			ps.directiveState = int(transactionDirectiveComment)
			return matchDirective, nil
		case ps.tokenComment:
			transaction.Comment = strings.TrimSpace(token.Value[1:]) // length enforced by tokenizer
			ps.directiveState = int(transactionDirectiveIndentOrNew)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected string, got %+v", token.Type)
		}
	case transactionDirectiveComment:
		switch token.Type {
		case ps.tokenComment:
			transaction.Comment = DeQuote(token.Value)
			ps.directiveState = int(transactionDirectiveIndentOrNew)
			return matchDirective, nil
		case ps.tokenNewline: // No comment
			ps.directiveState = int(transactionDirectiveIndentOrNew)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected comment, got %+v", token.Type)
		}
	case transactionDirectiveIndentOrNew:
		switch token.Type {
		case ps.tokenIndent:
			ps.directiveState = int(transactionDirectiveSubDirectiveFrom)
			return matchDirective, nil
		case ps.tokenNewline:
			if nextToken.Type == ps.tokenIndent || nextToken.Type == ps.tokenEOF {
				ps.directiveState = int(transactionDirectiveExpectIndent)
				return matchDirective, nil
			}
			return matchEntryHeader, nil // Finished commodity
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case transactionDirectiveExpectIndent:
		switch token.Type {
		case ps.tokenIndent:
			ps.directiveState = int(transactionDirectiveSubDirectiveFrom)
			return matchDirective, nil
		case ps.tokenDedent:
			return matchEntryHeader, nil // Finished movements
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case transactionDirectiveSubDirectiveFrom:
		switch token.Type {
		case ps.tokenIdent:
			m := Movement{From: token.Value}
			transaction.Movements = append(transaction.Movements, &m)
			ps.directiveState = int(transactionDirectiveSubDirectiveAmount)
			return matchDirective, nil
		case ps.tokenDedent:
			return matchEntryHeader, nil // Finished movements
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case transactionDirectiveSubDirectiveAmount:
		switch token.Type {
		case ps.tokenNumber:
			movement := transaction.Movements[len(transaction.Movements)-1]
			n, err := ParseNumber(token.Value)
			if err != nil {
				return matchEntryHeader, fmt.Errorf("expected number, got %+v", token.Value)
			}
			movement.Amount = n
			ps.directiveState = int(transactionDirectiveSubDirectiveArrow)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case transactionDirectiveSubDirectiveArrow:
		switch token.Type {
		case ps.tokenArrow:
			movement := transaction.Movements[len(transaction.Movements)-1]
			movement.Arrow = token.Value
			ps.directiveState = int(transactionDirectiveSubDirectiveTo)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case transactionDirectiveSubDirectiveTo:
		switch token.Type {
		case ps.tokenIdent:
			movement := transaction.Movements[len(transaction.Movements)-1]
			movement.To = token.Value
			ps.directiveState = int(transactionDirectiveSubDirectivesEnd)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case transactionDirectiveSubDirectivesEnd:
		switch token.Type {
		case ps.tokenNewline:
			ps.directiveState = int(transactionDirectiveSubDirectiveFrom)
			return matchDirective, nil
		case ps.tokenDedent:
			return matchEntryHeader, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	}
	return matchEntryHeader, nil
}

func init() {
	RegisterDirectiveNew("txn", NewTransactionDirective)
	RegisterDirectiveNew("*", NewTransactionDirective)
	RegisterDirectiveNew("transaction", NewTransactionDirective)
	RegisterDirectiveParser("txn", ParseTransactionDirective)
	RegisterDirectiveParser("*", ParseTransactionDirective)
	RegisterDirectiveParser("transaction", ParseTransactionDirective)
	RegisterDirectiveAdder("txn", AddTransactionDirective)
	RegisterDirectiveAdder("*", AddTransactionDirective)
	RegisterDirectiveAdder("transaction", AddTransactionDirective)
}

func NewTransactionDirective(entryHeader *EntryHeader, directive string, ps *parserState) {
	transaction := Transaction{
		EntryHeader: *entryHeader,
		Directive:   directive,
	}
	ps.entry = &transaction
}

func AddTransactionDirective(doc *Document, entry JournalEntry) error {
	// TODO: Add lookup on accounts
	transaction := entry.(*Transaction)
	doc.Transactions = append(doc.Transactions, transaction)
	return nil
}

func (t *Transaction) GetEntryHeader() *EntryHeader {
	return &t.EntryHeader
}

func (t *Transaction) GetFilename() string {
	return t.EntryHeader.Filename
}

func (t *Transaction) SetFilename(filename string) {
	t.EntryHeader.Filename = filename
}
