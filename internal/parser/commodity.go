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
	CommodityDetails []CommodityDetail `parser:"('INDENT' @@+ 'DEDENT')?"`
}

// Posting represents an account posting
type CommodityDetail struct {
	// eg Pound sterling
	Description string `parser:"( 'description' @String?"`
	// DescriptionComment string
	// How many of smallest unit makes up the unit
	// so for pre 1961 sterling it is 960 farthings or groats
	SubUnit int64 `parser:"| 'subunit' @Number?)"`
	// SubUnitComment string
}

func (a Commodity) Equal(b Commodity) bool {
	if a.Id != b.Id {
		return false
	}
	if len(a.CommodityDetails) != len(b.CommodityDetails) {
		return false
	}
	for i, cd := range a.CommodityDetails {
		if !cd.Equal(b.CommodityDetails[i]) {
			return false
		}
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
	sb.WriteString(c.Directive)
	sb.WriteString(" " + c.Id)
	for _, cd := range c.CommodityDetails {
		cd.ToStringBuider(sb)
	}
}

func (cd CommodityDetail) ToStringBuider(sb *strings.Builder) {
	sb.WriteString(cd.Description)
	sb.WriteString(strconv.FormatInt(cd.SubUnit, 10))
}
