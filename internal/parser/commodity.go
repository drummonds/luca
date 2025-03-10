package parser

import (
	"fmt"
	"strconv"
	"strings"

	"github.com/alecthomas/participle/v2/lexer"
)

// Commodity represents a currency or financial instrument
type Commodity struct {
	EntryHeader

	// Directive is "commodity" for commodity declarations
	Directive string `parser:"@('commodity')"`

	// Symbol is the commodity symbol/identifier
	Symbol string `parser:"@String"`

	// Name is the commodity name
	Name string `parser:"@String"`

	Description string `parser:"( 'description' @String)?"`
	// DescriptionComment string
	// How many of smallest unit makes up the unit
	// so for pre 1961 sterling it is 960 farthings or groats
	SubUnit int64 `parser:"( 'subunit' @Number)?"`
	// SubUnitComment string
}

func (a Commodity) Equal(b Commodity) bool {
	if a.Symbol != b.Symbol {
		return false
	}
	if a.Name != b.Name {
		return false
	}
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
	// Write header fields
	c.EntryHeader.ToStringBuilder(sb)

	// Add directive and symbol
	sb.WriteString(" ")
	sb.WriteString(c.Directive)
	sb.WriteString(" ")
	sb.WriteString(c.Symbol)
	sb.WriteString("\n")

	if c.Description != "" {
		sb.WriteString("\tdescription \"" + c.Description + "\"\n")
	}
	if c.SubUnit != 0 {
		sb.WriteString("\tsubunit " + strconv.FormatInt(c.SubUnit, 10) + "\n")
	}
}

// GetDirective returns the commodity directive type
func (c *Commodity) GetDirective() string {
	return c.Directive
}

func init() {
	RegisterDirectiveNew("commodity", NewCommodityDirective)
	RegisterDirectiveParser("commodity", ParseCommodityDirective)
	RegisterDirectiveAdder("commodity", AddCommodityDirective)
}

func NewCommodityDirective(entryHeader *EntryHeader, directive string, ps *parserState) {
	commodity := Commodity{
		EntryHeader: *entryHeader,
		Directive:   directive,
	}
	ps.entry = &commodity
}

type commodityDirectiveState int

const (
	commodityDirectiveLookForSymbol commodityDirectiveState = iota
	commodityDirectiveIndentOrNew
	commodityDirectiveExpectIndent // Know that that it is coming
	commodityDirectiveDetailStart
	commodityDirectiveDetailDescription
	commodityDirectiveDetailSubUnit
	commodityDirectiveDetailEnd
)

// Commodity = "commodity" <ident> ("INDENT" CommodityDetail "DEDENT")? .
// CommodityDetail = ("description" <string>)? ("subunit" <number>)? .
func ParseCommodityDirective(token lexer.Token, nextToken lexer.Token, ps *parserState) (parseState, error) {
	if ps.entry == nil {
		return matchEntryHeader, fmt.Errorf("entry must be initialised before parsing starts")
	}
	commodity := ps.entry.(*Commodity)
	switch commodityDirectiveState(ps.directiveState) {
	case commodityDirectiveLookForSymbol:
		switch token.Type {
		case ps.tokenIdent:
			commodity.Symbol = token.Value
			ps.directiveState = int(commodityDirectiveIndentOrNew)
			return matchDirective, nil
		case ps.tokenComment:
			///Ignore wait to add comment to commodity
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case commodityDirectiveIndentOrNew:
		switch token.Type {
		case ps.tokenNewline, ps.tokenEOF:
			if nextToken.Type == ps.tokenIndent {
				ps.directiveState = int(commodityDirectiveExpectIndent)
				return matchDirective, nil
			}
			return matchEntryHeader, nil // Finished commodity
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}

	case commodityDirectiveExpectIndent:
		switch token.Type {
		case ps.tokenIndent:
			ps.directiveState = int(commodityDirectiveDetailStart)
			return matchDirective, nil
		case ps.tokenDedent:
			return matchEntryHeader, nil // Finished commodity
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		}
	case commodityDirectiveDetailStart:
		switch token.Type {
		case ps.tokenIdent:
			value := strings.ToLower(token.Value)
			if value == "description" {
				ps.directiveState = int(commodityDirectiveDetailDescription)
				return matchDirective, nil
			}
			if value == "subunit" {
				ps.directiveState = int(commodityDirectiveDetailSubUnit)
				return matchDirective, nil
			}
			return matchEntryHeader, fmt.Errorf("unexpected commodity detail identifier, got %s", token.Value)
		case ps.tokenDedent:
			return matchEntryHeader, nil // Finished commodity
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token)
		}
	case commodityDirectiveDetailDescription:
		switch token.Type {
		case ps.tokenString:
			commodity.Description = DeQuote(token.Value)
			ps.directiveState = int(commodityDirectiveDetailEnd)
			return matchDirective, nil
		case ps.tokenNewline:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token.Type)
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token)
		}
	case commodityDirectiveDetailSubUnit:
		switch token.Type {
		case ps.tokenNumber:
			subUnit, err := strconv.ParseInt(token.Value, 10, 64)
			if err != nil {
				return matchEntryHeader, fmt.Errorf("expected number, got %+v", token)
			}
			commodity.SubUnit = subUnit
			ps.directiveState = int(commodityDirectiveDetailEnd)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token)
		}
	case commodityDirectiveDetailEnd:
		switch token.Type {
		case ps.tokenNewline:
			ps.directiveState = int(commodityDirectiveDetailStart)
			return matchDirective, nil
		default:
			return matchEntryHeader, fmt.Errorf("expected identifier, got %+v", token)
		}
	}
	return matchEntryHeader, nil
}

func AddCommodityDirective(doc *Document, entry JournalEntry) error {
	commodity := entry.(*Commodity)
	doc.Commodities = append(doc.Commodities, commodity)
	return nil
}

func (c *Commodity) GetEntryHeader() *EntryHeader {
	return &c.EntryHeader
}

func (c *Commodity) GetFilename() string {
	return c.EntryHeader.Filename
}

func (c *Commodity) SetFilename(filename string) {
	c.EntryHeader.Filename = filename
}
