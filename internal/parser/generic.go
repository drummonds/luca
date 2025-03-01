package parser

import (
	"strings"
)

// A generic format to illustrate the meta structure of an entry
type GenericEntry struct {
	Directive     string         `parser:" @'generic' "`
	Description   string         `parser:" (@String)?"`
	SubDirectives []SubDirective `parser:"('INDENT' @@+ 'DEDENT')?"`
}

// Posting represents an account posting
type SubDirective struct {
	Text string `parser:"@String"`
}

func (s SubDirective) ToStringBuider(sb *strings.Builder) {
	sb.WriteString(s.Text)
}

func (a SubDirective) Equal(b SubDirective) bool {
	return a.Text == b.Text
}

func (g GenericEntry) ToStringBuider(sb *strings.Builder) {
	sb.WriteString(g.Directive)
	if g.Description != "" {
		sb.WriteString(" " + g.Description)
	}
	for _, subDirective := range g.SubDirectives {
		subDirective.ToStringBuider(sb)
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
