package luca

import (
	"fmt"
	"strings"
	"time"

	"github.com/drummonds/luca/internal/datetime"
)

// This just descibes the data in the directive line which is common to all directives
// The entry part has all the extra arguments
type DirectiveHeader struct {
	ValueDate     time.Time
	KnowledgeDate *time.Time // nil if not present
	Name          string
	ExtraParams   string
	Comment       string
}

func (dd DirectiveHeader) GetValueDate() time.Time {
	return dd.ValueDate
}

func (dd DirectiveHeader) GetKnowledgeDate() *time.Time {
	return dd.KnowledgeDate
}
func (dd DirectiveHeader) GetName() string {
	return dd.Name
}
func (dd DirectiveHeader) GetExtraParams() string {
	return dd.ExtraParams
}
func (dd DirectiveHeader) GetComment() string {
	return dd.Comment
}

// Convert a simple directive to the first lines of the plain text
// Unit tested in commodity_test
func (d DirectiveHeader) String() string {
	// Get optional comment
	comment := d.GetComment()
	if comment != "" {
		comment = " // " + comment
	}
	// Get optinal knowledge date
	var kds string
	kd := d.GetKnowledgeDate()
	if kd != nil {
		kds = fmt.Sprintf("^%s ", datetime.LucaDateTimeString(*kd))
	}
	ep := d.GetExtraParams()
	if ep != "" {
		ep = " " + ep
	}
	cs := d.GetName()
	line := fmt.Sprintf("%s %s%s%s%s\n",
		datetime.LucaDateTimeString(d.ValueDate), kds, cs, ep, comment)
	return line
}

// Take a full line
func NewDirectiveHeader(line string) (directive DirectiveHeader, err error) {
	// split off comment
	part, comment := SplitComment(line)
	directive.Comment = comment
	// get value date
	parts := strings.SplitAfterN(part, " ", 2)
	if len(parts) != 2 { // at least have directive
		return DirectiveHeader{}, fmt.Errorf("invalid directive %s", line)
	}
	directive.ValueDate, err = datetime.ParseLucaDateTime(strings.TrimSpace(parts[0]))
	if err != nil {
		return DirectiveHeader{}, err
	}
	// check for knowledge date
	if strings.HasPrefix(strings.TrimSpace(parts[1]), "^") {
		parts = strings.SplitAfterN(strings.TrimSpace(parts[1]), " ", 2)
		if len(parts) != 2 { // at least have directive
			return DirectiveHeader{}, fmt.Errorf("invalid directive need knowledge date and name %s", line)
		}
		kd, err := datetime.ParseLucaDateTime(strings.TrimSpace(strings.Replace(parts[0], "^", "", 1)))
		if err != nil {
			return DirectiveHeader{}, fmt.Errorf("invalid knowledge date  %s, %+v", line, err)
		}
		directive.KnowledgeDate = &kd
	}
	// get name and extra params
	parts = strings.SplitAfterN(strings.TrimSpace(parts[1]), " ", 2)
	if len(parts) == 2 {
		directive.ExtraParams = strings.TrimSpace(strings.Replace(parts[1], "//", "", 1))
	}
	directive.Name = strings.ToLower(strings.TrimSpace(parts[0]))
	return directive, nil
}

func SplitComment(line string) (data, comment string) {
	parts := strings.SplitAfterN(line, "//", 2)
	data = strings.TrimSpace(parts[0])
	if len(parts) == 1 {
		data = strings.TrimSpace(parts[0])
		return
	}
	data = strings.TrimSpace(strings.Replace(parts[0], "//", "", 1))
	comment = strings.TrimSpace(strings.Replace(parts[1], "//", "", 1))
	return
}
