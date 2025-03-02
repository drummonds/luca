package parser

import "strings"

// An accounting Account
type Account struct {
	Directive      string        `parser:"@( 'open' )"`
	FullName       string        `parser:"@Ident?"`
	Commodity      string        `parser:"@Ident?"`
	AccountDetails AccountDetail `parser:"('INDENT' @@+ 'DEDENT')?"`
}

// AccountDetail represents additional account details
type AccountDetail struct {
	Description string `parser:"@String?"`
}

// AccountsEqual compares two Accounts for equality
func (a *Account) Equal(b *Account) bool {
	if a.Directive != b.Directive {
		return false
	}
	if a.FullName != b.FullName {
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

func (t Account) ToStringBuider(sb *strings.Builder) {
	sb.WriteString(" " + t.Directive)
	if t.FullName != "" {
		sb.WriteString(" " + t.FullName)
	}
	if t.Commodity != "" {
		sb.WriteString(" " + t.Commodity)
	}
	sb.WriteString("\n")
	t.AccountDetails.ToStringBuider(sb)
}

func (ad AccountDetail) ToStringBuider(sb *strings.Builder) {
	if ad.Description != "" {
		sb.WriteString("\t" + ad.Description + "\n")
	}
}
