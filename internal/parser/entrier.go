package parser

import (
	"strings"
	"time"
)

// Entrier is the interface that all entry types must implement
type Entrier interface {
	// ToStringBuilder writes the entry's string representation to the provided builder
	ToStringBuilder(sb *strings.Builder)

	// GetComments returns any comments associated with the entry
	GetComments() []string

	// GetDate returns the entry's date as a string
	GetDate() time.Time

	// GetKnowledgeDate returns when the entry was known/recorded
	GetKnowledgeDate() time.Time
}
