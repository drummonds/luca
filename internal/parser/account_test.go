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
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			b: Account{
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			want: true,
		},
		{
			name: "different full names",
			a: Account{
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			b: Account{
				Directive: "open",
				Name:      "assets:savings",
				Commodity: "USD",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			want: false,
		},
		{
			name: "different commodities",
			a: Account{
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			b: Account{
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "EUR",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			want: false,
		},
		{
			name: "different descriptions",
			a: Account{
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			b: Account{
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
				AccountDetails: AccountDetail{
					Description: "Savings Account",
				},
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

func TestAccountDetailEqual(t *testing.T) {
	tests := []struct {
		name string
		a    AccountDetail
		b    AccountDetail
		want bool
	}{
		{
			name: "identical account details",
			a: AccountDetail{
				Description: "Checking Account",
			},
			b: AccountDetail{
				Description: "Checking Account",
			},
			want: true,
		},
		{
			name: "different descriptions",
			a: AccountDetail{
				Description: "Checking Account",
			},
			b: AccountDetail{
				Description: "Savings Account",
			},
			want: false,
		},
		{
			name: "empty details",
			a:    AccountDetail{},
			b:    AccountDetail{},
			want: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.a.Equal(tt.b)
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
				Directive: "open",
				Name:      "assets:checking",
				Commodity: "USD",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			want: ` open assets:checking USD
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
			want: ` open assets:checking USD
`,
		},
		{
			name: "account without commodity",
			account: Account{
				Directive: "open",
				Name:      "assets:checking",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			want: ` open assets:checking
	description "Checking Account"
`,
		},
		{
			name: "account without full name",
			account: Account{
				Directive: "open",
				Commodity: "USD",
				AccountDetails: AccountDetail{
					Description: "Checking Account",
				},
			},
			want: ` open USD
	description "Checking Account"
`,
		},
		{
			name: "minimal account",
			account: Account{
				Directive: "open",
			},
			want: ` open
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

func TestAccountDetailToStringBuilder(t *testing.T) {
	tests := []struct {
		name   string
		detail AccountDetail
		want   string
	}{
		{
			name: "detail with description",
			detail: AccountDetail{
				Description: "Checking Account",
			},
			want: "\tdescription \"Checking Account\"\n",
		},
		{
			name:   "empty detail",
			detail: AccountDetail{},
			want:   "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var sb strings.Builder
			tt.detail.ToStringBuilder(&sb)
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
						Directive: "open",
						Name:      "assets:checking",
						Commodity: "USD",
						AccountDetails: AccountDetail{
							Description: "Checking Account",
						},
					},
				},
			},
			wantErr: false,
			debug:   true,
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
						Directive: "open",
						Name:      "assets:checking",
						AccountDetails: AccountDetail{
							Description: "Checking Account",
						},
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
						Directive: "open",
						Name:      "USD",
						AccountDetails: AccountDetail{
							Description: "Checking Account",
						},
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
	AbstractTestParse(t, tests)
}
