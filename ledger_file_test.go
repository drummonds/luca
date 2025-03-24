package luca

import (
	"fmt"
	"log"
	"testing"
	"time"

	"github.com/drummonds/luca/internal/parser"
	"github.com/shopspring/decimal"
	"github.com/spf13/afero"
	"github.com/stretchr/testify/assert"
)

const AFP1_TEST = `
2025-01-01 commodity GBP
2025-01-01 open equity:input
2025-01-01 open assets:cash

2024-03-21 txn "Investment"
	equity:input 25.00 -> assets:cash
`

// This is a test without saving as a file
func TestCanReadAFP1(t *testing.T) {
	var input string
	var name string
	input = AFP1_TEST
	name = "afp1.luca"
	// Read the input as string
	// Write the balance sheet
	// the summary in mermaid
	//save to a file
	// check read the file and save again and unchanged.

	doc, err := parser.Parse(input, name)
	if err != nil {
		log.Fatalf("Failed to parse: %v", err)
	}

	ledger, err := NewLedger()
	if err != nil {
		log.Fatalf("Failed to create ledger: %v", err)
	}
	assert.NoError(t, err)
	ledger.AddDocument(doc, name, true)
	// Write the balance sheet
	assert.Equal(t, ledger.DefaultCommodity.Symbol, "GBP")
	assert.Equal(t, 2, len(doc.Accounts))
	assert.Equal(t, 1, len(doc.Transactions))
	assert.Equal(t, 1, len(doc.Commodities))

	// Test Account
	accounts := doc.Accounts
	assert.Equal(t, "equity:input", accounts[0].Name)
	assert.Equal(t, "assets:cash", accounts[1].Name)
	assert.Equal(t, "afp1.luca", accounts[0].GetFilename())
	date, _ := time.Parse("2006-01-02", "2025-01-01")
	assert.Equal(t, date, accounts[0].GetDate())
}

func TestCanReadAFP1FromFile(t *testing.T) {
	// Setup in-memory filesystem
	fs := afero.NewMemMapFs()
	name := "afp1.luca"

	// Write test data to file in memory
	err := afero.WriteFile(fs, name, []byte(AFP1_TEST), 0644)
	assert.NoError(t, err)

	// Create new ledger from file using the memory filesystem
	ledger, err := NewLedgerFromFs(fs, ".", true)
	assert.NoError(t, err)

	// Verify the ledger contents
	assert.Equal(t, "GBP", ledger.DefaultCommodity.Symbol)
	assert.Equal(t, 2, len(ledger.Accounts))
	assert.Equal(t, 1, len(ledger.Transactions))
	assert.Equal(t, 1, len(ledger.Commodities))

	// Test Accounts
	accounts := ledger.Accounts
	assert.Equal(t, "equity:input", accounts[0].Name)
	assert.Equal(t, "assets:cash", accounts[1].Name)
	assert.Equal(t, name, accounts[0].GetFilename())
	date, _ := time.Parse("2006-01-02", "2025-01-01")
	assert.Equal(t, date, accounts[0].GetDate())

	balanceCheck := func(account *Account, expected decimal.Decimal) {
		assert.True(t, expected.Equal(account.BalanceLatest()),
			fmt.Sprintf("Balance of %s should be %s, but is %s",
				account.Name, expected.String(), account.BalanceLatest().String()))
	}
	// test account balances
	balanceCheck(accounts[0], decimal.NewFromInt(-25))
	balanceCheck(accounts[1], decimal.NewFromInt(25))
}
