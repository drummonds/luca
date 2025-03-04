package parser

import (
	"time"
)

// EntryDate contains the common date fields and comments that all entries share
type EntryDate struct {
	// Date when the transaction occurred
	Date time.Time `parser:"@Date"`

	// KnowledgeDate is when the transaction was recorded (optional)
	KnowledgeDate time.Time `parser:"[ @Date ]"`

	// Comments are any comment lines associated with this entry
	Comments []string `parser:"@Comment*"`
}

// GetDate returns the entry's date
func (e *EntryDate) GetDate() time.Time {
	return e.Date
}

// GetKnowledgeDate returns when the entry was known/recorded
func (e *EntryDate) GetKnowledgeDate() time.Time {
	return e.KnowledgeDate
}

// GetComments returns any comments associated with the entry
func (e *EntryDate) GetComments() []string {
	return e.Comments
}
