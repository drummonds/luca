package parser

import (
	"fmt"
	"strings"

	"github.com/alecthomas/participle/v2/lexer"
)

// A generic format to illustrate the meta structure of an entry
// This is not actually useful except in testing the generic portions
// of the parser.
type GenericEntry struct {
	EntryHeader

	Directive     string         `parser:" @'generic' "`
	Description   string         `parser:" (@String)?"`
	Comment       string         `parser:"@Comment?"`
	SubDirectives []SubDirective `parser:"('INDENT' @@+ 'DEDENT')?"`
}

// Posting represents an account posting
type SubDirective struct {
	Text string `parser:"@String"`
}

func (s SubDirective) ToStringBuilder(sb *strings.Builder) {
	sb.WriteString("\t" + `"` + s.Text + `"` + "\n")
}

func (a SubDirective) Equal(b SubDirective) bool {
	return a.Text == b.Text
}

func (g *GenericEntry) ToStringBuilder(sb *strings.Builder) {
	// Write header fields
	g.EntryHeader.ToStringBuilder(sb)

	// Add directive
	sb.WriteString(" ")
	sb.WriteString(g.Directive)

	// Add description if present
	if g.Description != "" {
		sb.WriteString(` "`)
		sb.WriteString(g.Description)
		sb.WriteString(`"`)
	}

	// Add comment if present
	if g.Comment != "" {
		sb.WriteString(` ; `)
		sb.WriteString(g.Comment)
	}

	sb.WriteString("\n")

	// Add subdirectives if any
	for _, subDirective := range g.SubDirectives {
		subDirective.ToStringBuilder(sb)
	}
}

func (a GenericEntry) Equal(b GenericEntry) bool {
	if a.Directive != b.Directive {
		return false
	}
	if a.Description != b.Description {
		return false
	}
	return ArrayEqual(a.SubDirectives, b.SubDirectives)
}

// GetDirective returns the directive name
func (g *GenericEntry) GetDirective() string {
	return g.Directive
}

type genericDirectiveState int

const (
	genericDirectiveStateStart genericDirectiveState = iota
	genericDirectiveComment
	genericDirectiveIndentOrNew
	genericDirectiveExpectIndent
	genericDirectiveSubDirectivesStart
	genericDirectiveSubDirectives
	genericDirectiveSubDirectivesEnd
)

// GenericEntry = "generic" <string>? <comment>? ("INDENT" SubDirective+ "DEDENT")? .
func ParseGenericDirective(token lexer.Token, nextToken lexer.Token, ps *parserState) (parseState, error) {
	if ps.entry == nil {
		return matchEntryHeader, fmt.Errorf("entry must be initialised before parsing starts")
	}
	generic := ps.entry.(*GenericEntry)
	switch genericDirectiveState(ps.directiveState) {
	case genericDirectiveStateStart:
		switch token.Type {
		case ps.tokenString:
			generic.Description = DeQuote(token.Value)
			ps.directiveState = int(genericDirectiveComment)
			return matchDirective, nil
		case ps.tokenString, ps.tokenNewline: // allow none
			ps.directiveState = int(genericDirectiveComment)
			return matchDirective, nil
		case ps.tokenComment:
			generic.Comment = strings.TrimSpace(token.Value[1:]) // length enforced by tokenizer
			ps.directiveState = int(genericDirectiveIndentOrNew)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected string, got %+v", token.Type)
		}
	case genericDirectiveComment:
		switch token.Type {
		case ps.tokenComment:
			generic.Comment = DeQuote(token.Value)
			ps.directiveState = int(genericDirectiveIndentOrNew)
			return matchDirective, nil
		case ps.tokenNewline: // No comment
			ps.directiveState = int(genericDirectiveIndentOrNew)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected comment, got %+v", token.Type)
		}
	case genericDirectiveIndentOrNew:
		switch token.Type {
		case ps.tokenIndent:
			ps.directiveState = int(genericDirectiveSubDirectives)
			return matchDirective, nil
		case ps.tokenNewline:
			if nextToken.Type == ps.tokenIndent || nextToken.Type == ps.tokenEOF {
				ps.directiveState = int(genericDirectiveExpectIndent)
				return matchDirective, nil
			}
			return matchEntryHeader, nil // Finished commodity
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}

	case genericDirectiveExpectIndent:
		switch token.Type {
		case ps.tokenIndent:
			ps.directiveState = int(genericDirectiveSubDirectives)
			return matchDirective, nil
		case ps.tokenDedent:
			return matchEntryHeader, nil // Finished commodity
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case genericDirectiveSubDirectives:
		switch token.Type {
		case ps.tokenString:
			generic.SubDirectives = append(generic.SubDirectives, SubDirective{Text: DeQuote(token.Value)})
			return matchDirective, nil
		case ps.tokenNewline:
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
	RegisterDirectiveNew("generic", NewGenericDirective)
	RegisterDirectiveParser("generic", ParseGenericDirective)
	RegisterDirectiveAdder("generic", AddGenericDirective)
}

func NewGenericDirective(entryHeader *EntryHeader, directive string, ps *parserState) {
	generic := GenericEntry{
		EntryHeader: *entryHeader,
		Directive:   directive,
	}
	ps.entry = &generic
}

func AddGenericDirective(doc *Document, entry JournalEntry) error {
	generic := entry.(*GenericEntry)
	doc.GenericEntries = append(doc.GenericEntries, generic)
	return nil
}

func (g *GenericEntry) GetEntryHeader() *EntryHeader {
	return &g.EntryHeader
}

func (g *GenericEntry) GetFilename() string {
	return g.EntryHeader.Filename
}

func (g *GenericEntry) SetFilename(filename string) {
	g.EntryHeader.Filename = filename
}
