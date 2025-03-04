package parser

import "strings"

// Document represents a complete financial document with multiple entries
type Document struct {
	// Entries contains all entries in the document
	Entries []Entrier
}

func (d Document) ToStringBuilder(sb *strings.Builder) {
	for _, entry := range d.Entries {
		entry.ToStringBuilder(sb)
	}
}

func (d Document) String() string {
	sb := strings.Builder{}
	d.ToStringBuilder(&sb)
	return sb.String()
}

// ToLines converts the document to a slice of strings
func (d *Document) ToLines() []string {
	var lines []string
	var sb strings.Builder

	for _, entry := range d.Entries {
		sb.Reset()
		entry.ToStringBuilder(&sb)
		lines = append(lines, sb.String())
	}

	return lines
}
