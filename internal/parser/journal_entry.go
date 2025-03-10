package parser

import (
	"strings"
)

// JournalEntry is the interface that all entry types must implement
type JournalEntry interface {
	ToStringBuilder(*strings.Builder)
	GetEntryHeader() *EntryHeader
	GetDirective() string
}

type JournalEntrier interface {
	Account | GenericEntry | Commodity | Transaction
}
