package parser

import (
	"testing"
)

func TestParseTransaction(t *testing.T) {
	tests := ParserTests{
		{
			name: "basic transaction",
			input: `2024-01-01 txn "Coffee shop"
    food  3.50 → assets:cash`,
			want: &Document{
				Entries: []*Entry{
					{
						Date: "2024-01-01",
						Transaction: &Transaction{
							Directive:   "txn",
							Description: "Coffee shop",
							Movements: []Movement{
								{
									From:   "food",
									To:     "assets:cash",
									Arrow:  "→",
									Amount: "3.50"},
							},
						},
					},
				},
			},
			wantErr: false,
		},
	}
	AbstractTestParse(t, tests)

}
