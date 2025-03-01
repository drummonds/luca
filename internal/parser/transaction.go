package parser

import "strings"

// An accounting transaction
type Transaction struct {
	Directive   string     `parser:"@( 'txn' | '*' )"`
	Description string     `parser:"@String?"`
	Movements   []Movement `parser:"('INDENT' @@+ 'DEDENT')?"`
}

// Posting represents an account posting
type Movement struct {
	From   string `parser:"@Ident"`
	Amount string `parser:"@Number"`
	Arrow  string `parser:"@Arrow"` // Store arrow type so can tround trip
	To     string `parser:"@Ident"`
}

// transactionsEqual compares two Transactions for equality
func (a *Transaction) Equal(b *Transaction) bool {
	if a.Directive != b.Directive {
		return false
	}
	if a.Description != b.Description {
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
	if a.Amount != b.Amount {
		return false
	}
	if a.Arrow != b.Arrow {
		return false
	}
	return true
}

func (t Transaction) ToStringBuider(sb *strings.Builder) {
	sb.WriteString(t.Directive)
	if t.Description != "" {
		sb.WriteString(" " + t.Description)
	}
	for _, movement := range t.Movements {
		movement.ToStringBuider(sb)
	}
}

func (m Movement) ToStringBuider(sb *strings.Builder) {
	sb.WriteString(m.From)
	sb.WriteString(m.Amount)
	sb.WriteString(m.Arrow)
	sb.WriteString(m.To)
}
