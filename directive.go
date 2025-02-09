package luca

import (
	"fmt"
	"time"

	"github.com/drummonds/luca/internal/datetime"
)

type Directive interface {
	Directive() string
	GetValueDate() time.Time
	GetKnowledgeDate() *time.Time
	GetIdComment() string
	GetComments() []string
}

// Convert a simple directive to the first lines of the plain text
// Unit tested in commodity_test
func DirectiveToLines(d Directive) []string {
	lines := []string{}
	// Add the comments
	comments := d.GetComments()
	if comments != nil {
		for _, comment := range d.GetComments() {
			lines = append(lines, fmt.Sprintf(";%s\n"), comment)
		}
	}
	var kds string
	kd := d.GetKnowledgeDate()
	if kd != nil {
		kds = " " + datetime.LucaDateTimeString(*kd)
	}
	cs := d.GetIdComment()
	if cs != "" {
		cs = " ;" + cs
	}
	lines = append(lines, fmt.Sprintf("%s%s%s\n"),
		datetime.LucaDateTimeString(*kd), kds, cs)
	return lines
}
