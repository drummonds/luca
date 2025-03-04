package luca

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/drummonds/luca/internal/parser"
)

type Ledger struct {
	Commodities    []parser.Commodity
	CommoditiesMap map[string]*parser.Commodity
	Accounts       []parser.Account
	AccountsMap    map[string]parser.Account
	Transactions   []parser.Transaction
}

func (l *Ledger) AddCommodity(entry parser.Entry) error {
	if entry.Commodity == nil {
		return fmt.Errorf("Can't add nil commodity to ledger")
	}
	if _, ok := l.CommoditiesMap[entry.Commodity.Id]; ok {
		return fmt.Errorf("commodity %s already exists in file", entry.Commodity.Id)
	}
	l.Commodities = append(l.Commodities, *entry.Commodity)
	l.CommoditiesMap[entry.Commodity.Id] = *entry.Commodity
}

func (l *Ledger) AddAccount(account parser.Account) {
	if account.Id == "" {
		return fmt.Errorf("Can't add account with empty id")
	}
	if _, ok := l.AccountsMap[account.Id]; ok {
		return fmt.Errorf("account %s already exists in file", account.Id)
	}
	l.Accounts = append(l.Accounts, account)
	l.AccountsMap[account.Id] = account
}

func (l *Ledger) Add(doc *parser.Document, filename string) {
	for _, entry := range doc.Entries {
		entry.Filename = filename
		if entry.Transaction != nil {
			entry.Filename = filename
			l.Transactions = append(l.Transactions, *entry.Transaction)
		}
		if entry.Commodity != nil {
			l.AddCommodity(*entry.Commodity)
		}
		if entry.Account != nil {
			entry.Filename = filename
			l.Accounts = append(l.Accounts, *entry.Account)
		}
	}
}

// Given a diretory read all the .luca files and return a Ledger
func NewLedger(dir string) (*Ledger, error) {
	files, err := filepath.Glob(filepath.Join(dir, "*.luca"))
	if err != nil {
		return nil, err
	}

	ledger := &Ledger{}
	for _, file := range files {
		content, err := os.ReadFile(file)
		if err != nil {
			return nil, err
		}
		doc, err := parser.Parse(string(content))
		if err != nil {
			return nil, err
		}
		ledger.Add(doc, file) //Add the file so that can reverse the aggregation
	}
	return ledger, nil
}
