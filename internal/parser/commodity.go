package parser

import (
	"strconv"
	"strings"
)

// An accounting transaction
type Commodity struct {
	EntryDate

	// Type is "commodity" for commodity declarations
	Type string `parser:"@('commodity')"`

	// Name is the commodity name
	Name string `parser:"@String"`

	// IdComment string
	CommodityDetail CommodityDetail `parser:"('INDENT' @@ 'DEDENT')?"`
}

// Posting represents an account posting
type CommodityDetail struct {
	// eg Pound sterling
	Description string `parser:"( 'description' @String)?"`
	// DescriptionComment string
	// How many of smallest unit makes up the unit
	// so for pre 1961 sterling it is 960 farthings or groats
	SubUnit int64 `parser:"( 'subunit' @Number)?"`
	// SubUnitComment string
}

func (a Commodity) Equal(b Commodity) bool {
	if a.Name != b.Name {
		return false
	}
	if a.CommodityDetail.Description != b.CommodityDetail.Description {
		return false
	}
	if a.CommodityDetail.SubUnit != b.CommodityDetail.SubUnit {
		return false
	}
	return true
}

func (a CommodityDetail) Equal(b CommodityDetail) bool {
	if a.Description != b.Description {
		return false
	}
	if a.SubUnit != b.SubUnit {
		return false
	}
	return true
}

// ToStringBuilder writes the commodity declaration to a string builder
func (c *Commodity) ToStringBuilder(sb *strings.Builder) {
	// Format date
	sb.WriteString(c.Date.Format("2006-01-02"))

	// Add knowledge date if present
	if !c.KnowledgeDate.IsZero() {
		sb.WriteString(" =")
		sb.WriteString(c.KnowledgeDate.Format("2006-01-02"))
	}

	// Add type and name
	sb.WriteString(" ")
	sb.WriteString(c.Type)
	sb.WriteString(" ")
	sb.WriteString(c.Name)
	sb.WriteString("\n")

	c.CommodityDetail.ToStringBuilder(sb)
}

func (cd CommodityDetail) ToStringBuilder(sb *strings.Builder) {
	if cd.Description != "" {
		sb.WriteString("\tdescription \"" + cd.Description + "\"\n")
	}
	if cd.SubUnit != 0 {
		sb.WriteString("\tsubunit " + strconv.FormatInt(cd.SubUnit, 10) + "\n")
	}
}
