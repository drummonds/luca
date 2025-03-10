package parser

import (
	"testing"
)

func TestParseTransaction(t *testing.T) {
	tests := ParserTests{
		{
			name: "basic transaction",
			input: `2024-01-01 txn "Coffee shop"
	food 3.50 → assets:cash
`,
			want: &Document{
				Transactions: []*Transaction{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive: "txn",
						Payee:     "Coffee shop",
						PostingStrings: []string{
							"food 3.50 → assets:cash",
						},
					},
				},
			},
			wantErr: false,
		},
	}
	AbstractTestParse(t, tests)
}
