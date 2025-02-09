package luca

import (
	"fmt"
	"io"
	"time"
)

var (
	// Commodities by Id
	Commodities         = map[string]*Commodity{}
	CommoditiesBySymbol = map[string]*Commodity{}
)

type Commodity struct {
	Comments       []string //Whole line comments
	ValueDate      time.Time
	KnowledgeDate  *time.Time //Optional
	Id             string     // eg GBP
	IdComment      string
	Name           string // eg Pound sterling
	NameComment    string
	SubUnit        int64 // how many decimal places to use
	SubUnitComment string
}

// Convert commodity to a string
func (c *Commodity) Directive() string {
	return "commodity"
}

func (c *Commodity) GetIdComment() string {
	return c.IdComment
}

func (c *Commodity) GetValueDate() time.Time {
	return c.ValueDate
}

func (c *Commodity) GetKnowledgeDate() *time.Time {
	return c.KnowledgeDate
}

// Convert commodity to a string
func (c *Commodity) GetComments() []string {
	return c.Comments
}

// Convert commodity to a string
func (c *Commodity) String() string {
	return c.Id
}

/*
;
892-01-01 commodity GBP

	name "Pound sterling"
	sub-unit 100
*/
func (c *Commodity) ToLines() []string {
	lines := DirectiveToLines(c)
	s := fmt.Sprintf("  name %s", c.Name)
	if c.NameComment != "" {
		s = " ;" + c.NameComment
	}
	lines = append(lines, s+"\n")
	s = fmt.Sprintf("  sub-unit %d", c.SubUnit)
	if c.SubUnitComment != "" {
		s = " ;" + c.SubUnitComment
	}
	lines = append(lines, s+"\n")
	return lines
}

func (c *Commodity) Write(w io.Writer) error {
	lines := c.ToLines()
	for _, line := range lines {
		_, err := io.WriteString(w, line)
		if err != nil {
			return err
		}
	}
	return nil
}

// var CommodityREX = rex.MustCompile(`(?P<commodity>[A-Za-z][\w]*)`)
// var commodityHeadREX = rex.MustCompile(`commodity\s+%s`, CommodityREX)
// var commodityBodyREX = rex.MustCompile(``+
// 	`(\s+note\s+(?P<note>.+))|`+
// 	`(\s+format\s+(?P<format>%s))|`+
// 	`(\s+(?P<nomarket>nomarket)\s*)|`+
// 	`(\s+symbol\s+(?P<symbol>[\w\.]+))|`+
// 	`(\s+(?P<default>default)\s*)`,
// 	AmountREX)

// func (p *Parser) parseCommodity(fn string) (*Commodity, error) {
// 	c := &Commodity{Decimals: 2, line: p.lineNr, file: fn}
// 	match := commodityHeadREX.Match(p.Bytes())
// 	c.Id = match["commodity"]
// 	for p.Scan() {
// 		line := p.Bytes()
// 		if len(bytes.TrimSpace(line)) == 0 || !unicode.IsSpace(rune(line[0])) {
// 			return c, nil
// 		}
// 		match = commodityBodyREX.Match(line)
// 		if match == nil {
// 			return c, fmt.Errorf("unrecognized commodity line: %s", p.Text())
// 		}
// 		if n := match["note"]; n != "" {
// 			c.Name = n
// 		} else if match["amount"] != "" {
// 			if f := match["decimals"]; len(f) == 0 {
// 				c.Decimals = 0
// 			} else {
// 				c.Decimals = len(f) - 1
// 			}
// 		} else if match["nomarket"] != "" {
// 			c.NoMarket = true
// 		} else if s := match["symbol"]; s != "" {
// 			c.Symbol = s
// 		} else if match["default"] != "" {
// 			DefaultCommodityId = c.Id
// 		} else {
// 			return c, fmt.Errorf("%s - failed to match commodity line: %s", c.Location(), p.Text())
// 		}
// 	}
// 	return c, p.Err()
// }

func (c *Commodity) includedIn(list []*Commodity) bool {
	for _, c2 := range list {
		if c == c2 {
			return true
		}
	}
	return false
}

// func (c *Commodity) MarshalJSON() ([]byte, error) {
// 	value := map[string]interface{}{
// 		"id":       c.Id,
// 		"name":     c.Name,
// 		"decimals": c.Decimals,
// 	}
// 	if c.Location() != "" {
// 		value["location"] = c.Location()
// 	}
// 	if c.Code != "" {
// 		value["code"] = c.Code
// 	}
// 	return json.MarshalIndent(value, "", "\t")
// }
