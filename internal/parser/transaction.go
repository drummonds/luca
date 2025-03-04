package parser

import "strings"

// An accounting transaction
type Transaction struct {
	EntryDate

	// Type is "txn" or "generic"
	Type string `parser:"@('txn' | 'generic')"`

	// Payee is the transaction description
	Payee string `parser:"@String"`

	// PostingStrings are the raw posting strings
	PostingStrings []string `parser:"(@String)*"`
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
	if a.Type != b.Type {
		return false
	}
	if a.Payee != b.Payee {
		return false
	}
	return ArrayEqual(a.PostingStrings, b.PostingStrings)
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

// ToStringBuilder writes the transaction to a string builder
func (t *Transaction) ToStringBuilder(sb *strings.Builder) {
	// Format date
	sb.WriteString(t.Date.Format("2006-01-02"))

	// Add knowledge date if present
	if !t.KnowledgeDate.IsZero() {
		sb.WriteString(" =")
		sb.WriteString(t.KnowledgeDate.Format("2006-01-02"))
	}

	// Add type and payee
	sb.WriteString(" ")
	sb.WriteString(t.Type)
	sb.WriteString(" ")
	sb.WriteString(t.Payee)
	sb.WriteString("\n")

	// Add postings
	for _, posting := range t.PostingStrings {
		sb.WriteString("    ")
		sb.WriteString(posting)
		sb.WriteString("\n")
	}
}

func (m Movement) ToStringBuilder(sb *strings.Builder) {
	sb.WriteString("\t")
	sb.WriteString(m.From + " ")
	sb.WriteString(m.Amount + " ")
	sb.WriteString(m.Arrow + " ")
	sb.WriteString(m.To)
	sb.WriteString("\n")
}
