package parser

import "strings"

// An accounting Account
type Account struct {
	Directive      string        `parser:"@( 'account' )"`
	Description    string        `parser:"@String?"`
	AccountDetails AccountDetail `parser:"('INDENT' @@+ 'DEDENT')?"`
}

// Posting represents an account posting
type AccountDetail struct {
	Commodity string `parser:"@Ident"?`
	FullName  string `parser:"@Ident"?`
}

// AccountsEqual compares two Accounts for equality
func (a *Account) Equal(b *Account) bool {
	if a.Directive != b.Directive {
		return false
	}
	if a.Description != b.Description {
		return false
	}
	return a.AccountDetails.Equal(b.AccountDetails)
}

func (a AccountDetail) Equal(b AccountDetail) bool {
	if a.Commodity != b.Commodity {
		return false
	}
	if a.FullName != b.FullName {
		return false
	}
	return true
}

func (t Account) ToStringBuider(sb *strings.Builder) {
	sb.WriteString(" " + t.Directive)
	if t.Description != "" {
		sb.WriteString(` "` + t.Description + `"`)
	}
	sb.WriteString("\n")
	if t.AccountDetails.Commodity != "" {
		sb.WriteString("\t" + t.AccountDetails.Commodity + " ")
	}
	if t.AccountDetails.FullName != "" {
		sb.WriteString(t.AccountDetails.FullName)
	}
}

func (ad AccountDetail) ToStringBuider(sb *strings.Builder) {
	if ad.Commodity != "" {
		sb.WriteString("\t" + ad.Commodity + "\n")
	}
	if ad.FullName != "" {
		sb.WriteString("\t" + ad.FullName + "\n")
	}
}
