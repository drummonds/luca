package parser

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestPreprocessIndentation(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		want    string
		wantErr bool
	}{
		{
			name: "basic indentation",
			input: `2024-01-01 txn
    expenses:food  50.00
    assets:bank   -50.00`,
			want: `2024-01-01 txn
INDENT expenses:food  50.00
assets:bank   -50.00
DEDENT`,
			wantErr: false,
		},
		{
			name: "multiple levels of indentation",
			input: `2024-01-01 txn
    expenses:food  50.00
        note "lunch"
    assets:bank   -50.00`,
			want: `2024-01-01 txn
INDENT expenses:food  50.00
INDENT note "lunch"
DEDENT assets:bank   -50.00
DEDENT`,
			wantErr: false,
		},
		{
			name: "invalid indentation",
			input: `2024-01-01 txn
    expenses:food  50.00
  assets:bank   -50.00`,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := PreprocessIndentation(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("PreprocessIndentation() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				assert.Equal(t, tt.want, got)
			}
		})
	}
}

type ParserTests []struct {
	name          string
	input         string
	expectedInput *string // "" is a valid expected input
	want          *Document
	wantErr       bool
	debug         bool
}

func AbstractTestParse(t *testing.T, tests ParserTests) {
	var (
		got *Document
		err error
	)
	for i, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.debug {
				got, err = ParseWithDebug(tt.input)
			} else {
				got, err = Parse(tt.input, "")
			}
			if err != nil {
				if tt.wantErr {
					return
				}
				t.Errorf("Parse() %d error = %v, wantErr %v", i, err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				assert.Equal(t, tt.want, got)
			}
			// Check closed loop
			if tt.expectedInput == nil {
				assert.Equal(t, tt.input, got.String(), "Input and output converted to string should be equal")
			} else {
				assert.Equal(t, *tt.expectedInput, got.String(), "Expected Input (different from input) and output converted to string should be equal")
			}
		})
	}
}

func TestDirectParsingToConcreteTypes(t *testing.T) {
	input := `2024-01-01 open assets:checking USD
2024-01-02 commodity USD
2024-01-03 txn "Grocery shopping"
	assets:cash 3.51 → food 
`
	doc, err := Parse(input, "test.luca")
	assert.NoError(t, err)
	assert.Equal(t, 1, len(doc.Accounts))
	assert.Equal(t, 1, len(doc.Transactions))
	assert.Equal(t, 1, len(doc.Commodities))

	// Test Account
	accounts := doc.Accounts
	assert.Equal(t, 1, len(accounts))
	assert.Equal(t, "open", accounts[0].GetDirective())
	assert.Equal(t, "assets:checking", accounts[0].Name)
	assert.Equal(t, "test.luca", accounts[0].GetFilename())
	date, _ := time.Parse("2006-01-02", "2024-01-01")
	assert.Equal(t, date, accounts[0].GetDate())

	// Test Commodity
	commodities := doc.Commodities
	assert.Equal(t, 1, len(commodities))
	assert.Equal(t, "commodity", commodities[0].GetDirective())
	assert.Equal(t, "USD", commodities[0].Symbol)

	// Test Transaction
	transactions := doc.Transactions
	assert.Equal(t, 1, len(transactions))
	assert.Equal(t, "txn", transactions[0].GetDirective())
	assert.Equal(t, 1, len(transactions[0].Movements))
}
