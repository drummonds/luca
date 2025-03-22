package luca

import (
	"fmt"
	"path/filepath"
	"strings"

	"github.com/drummonds/luca/internal/parser"
	"github.com/spf13/afero"
)

// A Ledger is a working list of all entries.
// Whereas the document is a list of all the entries in a raw form
type Ledger struct {
	// Raw data
	Commodities  []*parser.Commodity
	Accounts     []*parser.Account
	Transactions []*parser.Transaction
	// Helper data  Names are case insensitive
	CommoditiesMap   map[string]*parser.Commodity
	AccountsMap      map[string]*parser.Account
	DefaultCommodity *parser.Commodity
}

func (l *Ledger) AddCommodity(c *parser.Commodity) error {
	if c == nil {
		return fmt.Errorf("Can't add nil commodity to ledger")
	}
	if _, ok := l.CommoditiesMap[strings.ToLower(c.Symbol)]; ok {
		return fmt.Errorf("commodity %s already exists in file", c.Symbol)
	}
	l.Commodities = append(l.Commodities, c)
	l.CommoditiesMap[strings.ToLower(c.Symbol)] = c
	return nil
}

// CheckCommodity used when adding an account.
// This can auto create the commodity if it doesn't exist
// It is assumed that by this point that all the commodities have been added that have been specified.
// and supplies default values if meaningful in which case it returns true
func (l *Ledger) CheckCommoditySymbol(symbol string, autoCreate bool) (bool, error) {
	if symbol == "" {
		return false, fmt.Errorf("Can't add empty commodity to ledger")
	}
	symbolKey := strings.ToLower(symbol)
	if _, ok := l.CommoditiesMap[symbolKey]; ok {
		return false, nil
	}
	var c *parser.Commodity
	switch symbolKey {
	case "gbp":
		c = &parser.Commodity{
			Symbol:  "£",
			Name:    "British Pound",
			Sign:    "£",
			SubUnit: 100,
		}
	default:
		return false, fmt.Errorf("unknown commodity %s", symbol)
	}
	err := l.AddCommodity(c)
	if err != nil {
		return false, err
	}
	return true, nil
}

func (l *Ledger) AddAccount(a *parser.Account, autoCreate bool) error {
	if a == nil {
		return fmt.Errorf("can't add account with empty id")
	}
	_, err := l.CheckCommoditySymbol(a.Commodity, autoCreate)
	if err != nil {
		return err
	}
	// Now the commoddity is in place so can check and add the account
	if _, ok := l.AccountsMap[strings.ToLower(a.Name)]; ok {
		return fmt.Errorf("duplicate account %s already exists in file %s", a.Name, a.Filename)
	}
	l.Accounts = append(l.Accounts, a)
	l.AccountsMap[strings.ToLower(a.Name)] = a
	return nil
}

func (l *Ledger) CheckAccountName(name string, autoCreate bool) (bool, error) {
	if name == "" {
		return false, fmt.Errorf("can't add account with empty id")
	}
	if _, ok := l.AccountsMap[strings.ToLower(name)]; ok {
		return false, nil
	}
	if !autoCreate {
		return false, fmt.Errorf("account %s not found", name)
	}
	a := &parser.Account{
		Name: name,
	}
	err := l.AddAccount(a, autoCreate)
	if err != nil {
		return false, err
	}
	return true, nil
}

func (l *Ledger) AddTransaction(t *parser.Transaction, autoCreate bool) error {
	if t == nil {
		return fmt.Errorf("can't add transaction with empty id")
	}
	// Check that all the accounts are in place
	for _, m := range t.Movements {
		_, err := l.CheckAccountName(m.From, autoCreate)
		if err != nil {
			return err
		}
		_, err = l.CheckAccountName(m.To, autoCreate)
		if err != nil {
			return err
		}
	}
	// Now the accounts are in place can add transaction
	// Todo create sorted list of transactions
	l.Transactions = append(l.Transactions, t)
	return nil
}

// Assume that all entires are now in the document
// so if in mutiple files they need to be merged or added in
// sequence Commodities --> Accounts --> Transactions
func (l *Ledger) AddDocument(doc *parser.Document, filename string, autoCreate bool) error {
	var err error
	for _, c := range doc.Commodities {
		err = l.AddCommodity(c)
		if err != nil {
			return err
		}
	}
	l.SetDefaultCommodity()
	for _, a := range doc.Accounts {
		if a.Commodity == "" {
			a.Commodity = l.DefaultCommodity.Symbol
		}
		err = l.AddAccount(a, autoCreate)
		if err != nil {
			return err
		}
	}
	for _, t := range doc.Transactions {
		err = l.AddTransaction(t, autoCreate)
		if err != nil {
			return err
		}
	}
	return nil
}

// Given a directory read all the .luca files and return a Ledger
func NewLedger() (*Ledger, error) {
	ledger := &Ledger{}
	ledger.CommoditiesMap = make(map[string]*parser.Commodity)
	ledger.AccountsMap = make(map[string]*parser.Account)
	ledger.Commodities = make([]*parser.Commodity, 0)
	ledger.Accounts = make([]*parser.Account, 0)
	ledger.Transactions = make([]*parser.Transaction, 0)
	return ledger, nil
}

// Given a directory read all the .luca files and return a Ledger
func NewLedgerFrom(dir string, autoCreate bool) (*Ledger, error) {
	return NewLedgerFromFs(afero.NewOsFs(), dir, autoCreate)
}

// NewLedgerFromFs creates a new ledger from files in the given directory using the provided filesystem
func NewLedgerFromFs(fs afero.Fs, dir string, autoCreate bool) (*Ledger, error) {
	ledger, err := NewLedger()
	if err != nil {
		return nil, err
	}

	pattern := filepath.Join(dir, "*.luca")
	files, err := afero.Glob(fs, pattern)
	if err != nil {
		return nil, err
	}

	for _, file := range files {
		content, err := afero.ReadFile(fs, file)
		if err != nil {
			return nil, err
		}
		doc, err := parser.Parse(string(content), file)
		if err != nil {
			return nil, err
		}
		ledger.AddDocument(doc, file, autoCreate)
	}
	return ledger, nil
}

// SetDefaultCommodity checks for a single default commodity and sets it
func (l *Ledger) SetDefaultCommodity() error {
	switch len(l.Commodities) {
	case 0:
		// If no commodities, create GBP as default
		gbp := &parser.Commodity{
			Symbol:  "GBP",
			Name:    "British Pound",
			Sign:    "£",
			SubUnit: 100,
			Default: true,
		}
		if err := l.AddCommodity(gbp); err != nil {
			return err
		}
		l.DefaultCommodity = gbp
		return nil
	case 1:
		// If only one commodity, make it default
		l.Commodities[0].Default = true
		l.DefaultCommodity = l.Commodities[0]
		return nil
	default:
		// Original logic for multiple commodities
		var defaultCommodity *parser.Commodity
		for _, c := range l.Commodities {
			if c.Default {
				if defaultCommodity != nil {
					return fmt.Errorf("multiple default commodities found: %s and %s",
						defaultCommodity.Symbol, c.Symbol)
				}
				defaultCommodity = c
			}
		}

		if defaultCommodity != nil {
			if l.DefaultCommodity != nil && l.DefaultCommodity != defaultCommodity {
				return fmt.Errorf("conflicting default commodity: existing %s vs new %s",
					l.DefaultCommodity.Symbol, defaultCommodity.Symbol)
			}
			l.DefaultCommodity = defaultCommodity
		}
	}

	return nil
}
