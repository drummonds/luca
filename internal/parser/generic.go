package parser

import (
	"strings"
)

// A generic format to illustrate the meta structure of an entry
// This is not actually useful except in testing the generic portions
// of the parser.
type GenericEntry struct {
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

func (g GenericEntry) ToStringBuilder(sb *strings.Builder) {
	sb.WriteString(" " + g.Directive)
	if g.Description != "" {
		sb.WriteString(` "` + g.Description + `"`)
	}
	if g.Comment != "" {
		sb.WriteString(` ; ` + g.Comment)
	}
	sb.WriteString("\n")
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
