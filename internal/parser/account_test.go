package parser

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestAccountEqual(t *testing.T) {
	tests := []struct {
		name string
		a    Account
		b    Account
		want bool
	}{
		{
			name: "identical accounts",
			a: Account{
				Directive:   "open",
				Name:        "assets:checking",
				Commodity:   "USD",
				Description: "Checking Account",
			},
			b: Account{
				Directive:   "open",
				Name:        "assets:checking",
				Commodity:   "USD",
				Description: "Checking Account",
			},
			want: true,
		},
		{
			name: "different full names",
			a: Account{
				Directive:   "open",
				Name:        "assets:checking",
				Commodity:   "USD",
				Description: "Checking Account",
			},
			b: Account{
				Directive:   "open",
				Name:        "assets:savings",
				Commodity:   "USD",
				Description: "Checking Account",
			},
			want: false,
		},
		{
			name: "different commodities",
			a: Account{
				Directive:   "open",
				Name:        "assets:checking",
				Commodity:   "USD",
				Description: "Checking Account",
			},
			b: Account{
				Directive:   "open",
				Name:        "assets:checking",
				Commodity:   "EUR",
				Description: "Checking Account",
			},
			want: false,
		},
		{
			name: "different descriptions",
			a: Account{
				Directive:   "open",
				Name:        "assets:checking",
				Commodity:   "USD",
				Description: "Checking Account",
			},
			b: Account{
				Directive:   "open",
				Name:        "assets:checking",
				Commodity:   "USD",
				Description: "Savings Account",
			},
			want: false,
		},
		{
			name: "empty details",
			a: Account{
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
			},
			b: Account{
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
			},
			want: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.a.Equal(&tt.b)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestAccountToStringBuilder(t *testing.T) {
	tests := []struct {
		name    string
		account Account
		want    string
	}{
		{
			name: "complete account",
			account: Account{
				Directive:   "open",
				Name:        "assets:checking",
				Commodity:   "USD",
				Description: "Checking Account",
			},
			want: `0001-01-01 open assets:checking USD
	description "Checking Account"
`,
		},
		{
			name: "account without description",
			account: Account{
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
			},
			want: `0001-01-01 open assets:checking USD
`,
		},
		{
			name: "account without commodity",
			account: Account{
				Directive:   "open",
				Name:        "assets:checking",
				Description: "Checking Account",
			},
			want: `0001-01-01 open assets:checking
	description "Checking Account"
`,
		},
		{
			// I don't like this case as it is wrong not have a full name
			// But if there isn't then this tests that to string builder works
			name: "account without full name",
			account: Account{
				Directive:   "open",
				Commodity:   "USD",
				Description: "Checking Account",
			},
			want: `0001-01-01 open USD
	description "Checking Account"
`,
		},
		{
			name: "minimal account",
			account: Account{
				Directive: "open",
			},
			want: `0001-01-01 open
`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var sb strings.Builder
			tt.account.ToStringBuilder(&sb)
			got := sb.String()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestParseAccount(t *testing.T) {
	tests := ParserTests{
		{
			name: "basic account",
			input: `2024-01-01 open assets:checking USD
	description "Checking Account"
`,
			want: &Document{
				Accounts: []*Account{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive:   "open",
						Name:        "assets:checking",
						Commodity:   "USD",
						Description: "Checking Account",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "account without description",
			input: `2024-01-01 open assets:checking USD
`,
			want: &Document{
				Accounts: []*Account{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive: "open",
						Name:      "assets:checking",
						Commodity: "USD",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "account without commodity",
			input: `2024-01-01 open assets:checking
	description "Checking Account"
`,
			want: &Document{
				Accounts: []*Account{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive:   "open",
						Name:        "assets:checking",
						Description: "Checking Account",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "account without full name",
			input: `2024-01-01 open USD
	description "Checking Account"
`,
			want: &Document{
				Accounts: []*Account{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive:   "open",
						Name:        "USD",
						Description: "Checking Account",
					},
				},
			},
			wantErr: true,
		},
		{
			name: "minimal account",
			input: `2024-01-01 open
`,
			want: &Document{
				Accounts: []*Account{{
					EntryHeader: EntryHeader{
						Date: ParseDate("2024-01-01"),
					},
					Directive: "open",
				}},
			},
			wantErr: true,
		},
	}
	AbstractTestParse(t, tests[0:1])
}
