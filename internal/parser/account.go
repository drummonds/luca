package parser

import (
	"fmt"
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

	Commodity   string `parser:"@Ident?"`
	Description string
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
	return a.Description == b.Description
}

// ToStringBuilder writes the account declaration to a string builder
func (a *Account) ToStringBuilder(sb *strings.Builder) {
	// Write header fields
	a.EntryHeader.ToStringBuilder(sb)

	// Add directive and name
	sb.WriteString(" ")
	sb.WriteString(a.Directive)
	if a.Name != "" {
		sb.WriteString(" ")
		sb.WriteString(a.Name)
	}

	// Add commodity if present
	if a.Commodity != "" {
		sb.WriteString(" ")
		sb.WriteString(a.Commodity)
	}

	sb.WriteString("\n")

	// Add detailed fields if any
	if a.Description != "" {
		sb.WriteString("\tdescription \"" + a.Description + "\"\n")
	}
}

// GetDirective returns the account directive type
func (a *Account) GetDirective() string {
	return a.Directive
}

type accountDirectiveState int

const (
	accountDirectiveLookForName accountDirectiveState = iota
	accountDirectiveLookForCommodity
	accountDirectiveIndentOrNew
	accountDirectiveExpectIndent // Know that that it is coming
	accountDirectiveDetailStart
	accountDirectiveDetailDescription
	accountDirectiveDetailEnd
)

// Account = "open" <ident> <ident> ("INDENT" AccountDetail "DEDENT")? .
func ParseAccountDirective(token lexer.Token, nextToken lexer.Token, ps *parserState) (parseState, error) {
	if ps.entry == nil {
		return matchEntryHeader, fmt.Errorf("entry must be initialised before parsing starts")
	}
	account := ps.entry.(*Account)
	switch accountDirectiveState(ps.directiveState) {
	case accountDirectiveLookForName:
		switch token.Type {
		case ps.tokenIdent:
			account.Name = token.Value
			ps.directiveState = int(accountDirectiveLookForCommodity)
			return matchDirective, nil
		case ps.tokenComment:
			///Ignore wait to add comment to account
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case accountDirectiveLookForCommodity:
		switch token.Type {
		case ps.tokenIdent:
			account.Commodity = token.Value
			ps.directiveState = int(accountDirectiveIndentOrNew)
			return matchDirective, nil
		case ps.tokenComment:
			///Ignore wait to add comment to account
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case accountDirectiveIndentOrNew:
		switch token.Type {
		case ps.tokenNewline, ps.tokenEOF:
			if nextToken.Type == ps.tokenIndent {
				ps.directiveState = int(accountDirectiveExpectIndent)
				return matchDirective, nil
			}
			return matchEntryHeader, nil // Finished account
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case accountDirectiveExpectIndent:
		switch token.Type {
		case ps.tokenIndent:
			ps.directiveState = int(accountDirectiveDetailStart)
			return matchDirective, nil
		case ps.tokenDedent:
			return matchEntryHeader, nil // Finished account
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case accountDirectiveDetailStart:
		switch token.Type {
		case ps.tokenIdent:
			value := strings.ToLower(token.Value)
			if value == "description" {
				ps.directiveState = int(accountDirectiveDetailDescription)
				return matchDirective, nil
			}
			return matchEntryHeader, fmt.Errorf("unexpected account detail identifier, got %s", token.Value)
		case ps.tokenDedent:
			return matchEntryHeader, nil // Finished account
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token)
		}
	case accountDirectiveDetailDescription:
		switch token.Type {
		case ps.tokenString:
			account.Description = DeQuote(token.Value)
			ps.directiveState = int(accountDirectiveDetailEnd)
			return matchDirective, nil
		case ps.tokenNewline:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token)
		}
	case accountDirectiveDetailEnd:
		switch token.Type {
		case ps.tokenNewline:
			ps.directiveState = int(accountDirectiveDetailStart)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token)
		}
	}
	return matchEntryHeader, nil
}

func init() {
	RegisterDirectiveNew("open", NewAccountDirective)
	RegisterDirectiveParser("open", ParseAccountDirective)
	RegisterDirectiveAdder("open", AddAccountDirective)
}

func NewAccountDirective(entryHeader *EntryHeader, directive string, ps *parserState) {
	account := Account{
		EntryHeader: *entryHeader,
		Directive:   directive,
	}
	ps.entry = &account
}

func AddAccountDirective(doc *Document, entry JournalEntry) error {
	// TODO: Add lookup on accounts
	account := entry.(*Account)
	doc.Accounts = append(doc.Accounts, account)
	return nil
}

func (a *Account) GetEntryHeader() *EntryHeader {
	return &a.EntryHeader
}

func (a *Account) GetFilename() string {
	return a.EntryHeader.Filename
}

func (a *Account) SetFilename(filename string) {
	a.EntryHeader.Filename = filename
}
