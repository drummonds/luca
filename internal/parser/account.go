package parser

import "strings"

// An accounting Account
type Account struct {
	EntryDate

	// Type is "open" for account declarations
	Type string `parser:"@('open')"`

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
	if a.Type != b.Type {
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
	// Format date
	sb.WriteString(a.Date.Format("2006-01-02"))

	// Add knowledge date if present
	if !a.KnowledgeDate.IsZero() {
		sb.WriteString(" =")
		sb.WriteString(a.KnowledgeDate.Format("2006-01-02"))
	}

	// Add type and name
	sb.WriteString(" ")
	sb.WriteString(a.Type)
	sb.WriteString(" ")
	sb.WriteString(a.Name)
	sb.WriteString("\n")

	if a.Commodity != "" {
		sb.WriteString(" " + a.Commodity)
	}
	sb.WriteString("\n")

	a.AccountDetails.ToStringBuilder(sb)
}

func (ad AccountDetail) ToStringBuilder(sb *strings.Builder) {
	if ad.Description != "" {
		sb.WriteString("\tdescription \"" + ad.Description + "\"\n")
	}
}
