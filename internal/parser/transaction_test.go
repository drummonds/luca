package parser

import (
	"testing"

	"github.com/shopspring/decimal"
)

func TestParseTransaction(t *testing.T) {
	tests := ParserTests{
		{
			name: "basic transaction",
			input: `2024-01-01 txn "Coffee shop"
	food 3.51 → assets:cash
`,
			want: &Document{
				Transactions: []*Transaction{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive:   "txn",
						Description: "Coffee shop",
						Movements: []*Movement{{
							From:   "food",
							Amount: decimal.NewFromFloat(3.51),
							Arrow:  "→",
							To:     "assets:cash",
						}},
					},
				},
			},
			wantErr: false,
		},
	}
	AbstractTestParse(t, tests)
}
