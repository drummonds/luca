package parser

import (
	"strconv"
	"strings"
)

// An accounting transaction
type Commodity struct {
	Directive string `parser:"@'commodity'"`
	Id        string `parser:"@Ident"`
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
	if a.Id != b.Id {
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

func (c Commodity) ToStringBuider(sb *strings.Builder) {
	sb.WriteString(" " + c.Directive)
	sb.WriteString(" " + c.Id + "\n")
	c.CommodityDetail.ToStringBuider(sb)
}

func (cd CommodityDetail) ToStringBuider(sb *strings.Builder) {
	if cd.Description != "" {
		sb.WriteString("\tdescription \"" + cd.Description + "\"\n")
	}
	if cd.SubUnit != 0 {
		sb.WriteString("\tsubunit " + strconv.FormatInt(cd.SubUnit, 10) + "\n")
	}
}
