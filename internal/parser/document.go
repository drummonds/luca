package parser

import "strings"

// Document represents the entire file
type Document struct {
	Entries []*Entry `parser:"@@*"`
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

func (d Document) ToLines() []string {
	return strings.Split(d.String(), "\n")
}
