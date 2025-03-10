package parser

import (
	"strings"

	"github.com/alecthomas/participle/v2/lexer"
)

// An accounting Account
type Account struct {
	EntryHeader

	// Directive is "open" for account declarations
	Directive string `parser:"@('open')"`

	// Name is the account name
	Name string `parser:"@String"`

	Commodity      string        `parser:"@Ident?"`
	AccountDetails AccountDetail `parser:"('INDENT' @@ 'DEDENT')?"`
}

// AccountDetail represents additional account details
type AccountDetail struct {
	Description string `parser:"( 'description' @String)?"`
}

// AccountsEqual compares two Accounts for equality
func (a *Account) Equal(b *Account) bool {
	if a.Directive != b.Directive {
		return false
	}
	if a.Name != b.Name {
		return false
	}
	if a.Commodity != b.Commodity {
		return false
	}
	return a.AccountDetails.Equal(b.AccountDetails)
}

func (a AccountDetail) Equal(b AccountDetail) bool {
	if a.Description != b.Description {
		return false
	}
	return true
}

// ToStringBuilder writes the account declaration to a string builder
func (a *Account) ToStringBuilder(sb *strings.Builder) {
	// Write header fields
	a.EntryHeader.ToStringBuilder(sb)

	// Add directive and name
	sb.WriteString(" ")
	sb.WriteString(a.Directive)
	sb.WriteString(" ")
	sb.WriteString(a.Name)

	// Add commodity if present
	if a.Commodity != "" {
		sb.WriteString(" ")
		sb.WriteString(a.Commodity)
	}

	sb.WriteString("\n")

	// Add detailed fields if any
	if a.AccountDetails.Description != "" {
		a.AccountDetails.ToStringBuilder(sb)
	}
}

func (ad AccountDetail) ToStringBuilder(sb *strings.Builder) {
	if ad.Description != "" {
		sb.WriteString("\tdescription \"" + ad.Description + "\"\n")
	}
}

// GetDirective returns the account directive type
func (a *Account) GetDirective() string {
	return a.Directive
}
func init() {
	RegisterDirectiveParser("open", ParseAccountDirective)
}

func ParseAccountDirective(token lexer.Token, nextToken lexer.Token, ps *parserState) (parseState, error) {
	return matchDirective, nil
}
