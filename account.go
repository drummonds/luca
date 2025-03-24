package luca

import (
	"fmt"
	"sort"
	"strings"

	"github.com/drummonds/luca/internal/parser"
	"github.com/shopspring/decimal"
)

type movementSlice []*Movement

type Movement struct {
	parser.Movement
	transaction *parser.Transaction
}

// Len is part of sort.Interface.
func (m movementSlice) Len() int {
	return len(m)
}

// Swap is part of sort.Interface.
func (m movementSlice) Swap(i, j int) {
	m[i], m[j] = m[j], m[i]
}

// Less is part of sort.Interface. We use count as the value to sort by
func (m movementSlice) Less(i, j int) bool {
	if m[i].transaction.Date != m[j].transaction.Date {
		return m[i].transaction.Date.Before(m[j].transaction.Date)
	}
	if m[i].transaction.KnowledgeDate != m[j].transaction.KnowledgeDate {
		return m[i].transaction.KnowledgeDate.Before(m[j].transaction.KnowledgeDate)
	}
	if m[i].Amount != m[j].Amount {
		return m[i].Amount.LessThan(m[j].Amount)
	}
	return m[i].transaction.Description < m[j].transaction.Description
}

type Account struct {
	*parser.Account
	Ledger    *Ledger
	movements movementSlice
}

func AccountNameToList(name string) []string {
	parts := strings.Split(name, ":")
	for i, part := range parts {
		parts[i] = strings.TrimSpace(part)
	}
	return parts
}

func ValidateAccount(account *parser.Account, ledger *Ledger) (*parser.Account, error) {
	errorMessage := []string{}
	// validate name is valid
	parts := AccountNameToList(account.Name)
	switch len(parts) {
	case 0:
		errorMessage = append(errorMessage, fmt.Sprintf("account name is blank and so invalid from file %s", account.Filename))
	default:
		rootName := strings.ToLower(parts[0])
		switch rootName {
		case "assets", "liabilities", "equity", "income", "expenses":
		default:
			errorMessage = append(
				errorMessage,
				fmt.Sprintf("first part of account name %s must be one of assets, liabilities, equity, income, or expenses from file %s,", account.Name, account.Filename),
			)
		}
	}
	if len(errorMessage) == 0 {
		return account, nil
	}
	return account, fmt.Errorf(strings.Join(errorMessage, ", "))
}

func NewAccount(account *parser.Account, ledger *Ledger) (*Account, error) {
	account, err := ValidateAccount(account, ledger)
	if err != nil {
		return nil, err
	}

	a := &Account{
		Account: account,
		Ledger:  ledger,
	}
	a.movements = make(movementSlice, 0)
	return a, nil
}

func (a *Account) LinkMovement(pm *parser.Movement, tx *parser.Transaction) error {
	m := &Movement{
		Movement:    *pm,
		transaction: tx,
	}
	a.movements = append(a.movements, m)
	return nil
}

func (a *Account) SortMovements() {
	sort.Sort(a.movements)
}

func (a *Account) BalanceLatest() decimal.Decimal {
	balance := decimal.Zero
	for _, m := range a.movements {
		if m.From == a.Name {
			balance = balance.Sub(m.Amount)
		} else {
			balance = balance.Add(m.Amount)
		}
	}
	return balance
}
