package parser

import (
	"fmt"
	"strings"
	"time"

	"github.com/alecthomas/participle/v2/lexer"
)

// EntryHeader contains the common fields that all entries share
type EntryHeader struct {
	// Date when the transaction occurred
	Date time.Time `parser:"@Date"`

	// KnowledgeDate is when the transaction was recorded (optional)
	KnowledgeDate time.Time `parser:"[ '=' @Date ]"`

	// Comments are any comment lines associated with this entry
	Comments []string `parser:"( @Comment* )"`

	// Filename is the source file this entry came from (not parsed, set by the parser)
	Filename string
}

// GetDate returns the entry's date
func (e *EntryHeader) GetDate() time.Time {
	return e.Date
}

// GetKnowledgeDate returns when the entry was known/recorded
func (e *EntryHeader) GetKnowledgeDate() time.Time {
	return e.KnowledgeDate
}

// GetComments returns any comments associated with the entry
func (e *EntryHeader) GetComments() []string {
	return e.Comments
}

// GetFilename returns the source filename this entry came from
func (e *EntryHeader) GetFilename() string {
	return e.Filename
}

// SetFilename sets the source filename
func (e *EntryHeader) SetFilename(filename string) {
	e.Filename = filename
}

// ToStringBuilder writes the common header fields to a string builder
func (e *EntryHeader) ToStringBuilder(sb *strings.Builder) {
	// Write comments if any
	for _, comment := range e.Comments {
		sb.WriteString("; ")
		sb.WriteString(comment)
		sb.WriteString("\n")
	}

	// Format date
	sb.WriteString(e.Date.Format("2006-01-02"))

	// Add knowledge date if present
	if !e.KnowledgeDate.IsZero() {
		sb.WriteString(" ^")
		sb.WriteString(e.KnowledgeDate.Format("2006-01-02"))
	}
}

// Entry = <comment>* <date> <knowledgedate>? <directive>
func parseEntryHeader(token lexer.Token, nextToken lexer.Token, ps *parserState, thisEntryHeader *EntryHeader) (parseState, string, error) {
	switch token.Type {
	case ps.tokenDate:
		thisEntryHeader.Date = ParseDate(token.Value)
	case ps.tokenKnowledgeDate:
		thisEntryHeader.KnowledgeDate = ParseDate(token.Value[1:])
	case ps.tokenIdent:
		directive := token.Value
		return matchDirective, directive, nil
	case ps.tokenComment:
		comment := strings.TrimSpace(token.Value[1:]) // length enforced by tokenizer
		thisEntryHeader.Comments = append(thisEntryHeader.Comments, comment)
	case ps.tokenNewline:
		// ignore
	default:
		return matchEntryHeader, "", fmt.Errorf("unknown token type: %+v when parsing entry header", token.Type)
	}
	return matchEntryHeader, "", nil
}
