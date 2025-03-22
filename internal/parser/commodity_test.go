package parser

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCommodityEqual(t *testing.T) {
	tests := []struct {
		name string
		a    Commodity
		b    Commodity
		want bool
	}{
		{
			name: "identical commodities",
			a: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     100,
			},
			b: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     100,
			},
			want: true,
		},
		{
			name: "different IDs",
			a: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     100,
			},
			b: Commodity{
				Directive:   "commodity",
				Symbol:      "EUR",
				Description: "US Dollar",
				SubUnit:     100,
			},
			want: false,
		},
		{
			name: "different descriptions",
			a: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     100,
			},
			b: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "United States Dollar",
				SubUnit:     100,
			},
			want: false,
		},
		{
			name: "different subunits",
			a: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     100,
			},
			b: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     1000,
			},
			want: false,
		},
		{
			name: "different default",
			a: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     100,
				Default:     true,
			},
			b: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     1000,
			},
			want: false,
		},
		{
			name: "same default",
			a: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     100,
				Default:     true,
			},
			b: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     100,
				Default:     true,
			},
			want: true,
		},
		{
			name: "empty details",
			a: Commodity{
				Directive: "commodity",
				Symbol:    "USD",
			},
			b: Commodity{
				Directive: "commodity",
				Symbol:    "USD",
			},
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

func TestCommodityToStringBuilder(t *testing.T) {
	tests := []struct {
		name      string
		commodity Commodity
		want      string
	}{
		{
			name: "full commodity",
			commodity: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
				SubUnit:     100,
			},
			want: "0001-01-01 commodity USD\n\tdescription \"US Dollar\"\n\tsubunit 100\n",
		},
		{
			name: "commodity without description",
			commodity: Commodity{
				Directive: "commodity",
				Symbol:    "USD",
				SubUnit:   100,
			},
			want: "0001-01-01 commodity USD\n\tsubunit 100\n",
		},
		{
			name: "commodity without subunit",
			commodity: Commodity{
				Directive:   "commodity",
				Symbol:      "USD",
				Description: "US Dollar",
			},
			want: "0001-01-01 commodity USD\n\tdescription \"US Dollar\"\n",
		},
		{
			name: "minimal commodity",
			commodity: Commodity{
				Directive: "commodity",
				Symbol:    "USD",
			},
			want: "0001-01-01 commodity USD\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var sb strings.Builder
			tt.commodity.ToStringBuilder(&sb)
			got := sb.String()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestParseCommodity(t *testing.T) {
	tests := ParserTests{
		{
			name: "full commodity",
			input: `2024-01-01 commodity USD
	description "US Dollar"
	subunit 100
`,
			want: &Document{
				Commodities: []*Commodity{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive:   "commodity",
						Symbol:      "USD",
						Description: "US Dollar",
						SubUnit:     100,
					},
				},
			},
			wantErr: false,
			debug:   false,
		},
		{
			name: "commodity without description",
			input: `2024-01-01 commodity USD
	subunit 100
`,
			want: &Document{
				Commodities: []*Commodity{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive: "commodity",
						Symbol:    "USD",
						SubUnit:   100,
					},
				},
			},
			wantErr: false,
		},
		{
			name: "commodity without subunit",
			input: `2024-01-01 commodity USD
	description "US Dollar"
`,
			want: &Document{
				Commodities: []*Commodity{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive:   "commodity",
						Symbol:      "USD",
						Description: "US Dollar",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "minimal commodity",
			input: `2024-01-01 commodity USD
`,
			want: &Document{
				Commodities: []*Commodity{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive: "commodity",
						Symbol:    "USD",
					},
				},
			},
			wantErr: false,
		},
	}
	AbstractTestParse(t, tests)
}

func TestCommodityDefault(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected *Commodity
		wantErr  bool
	}{
		{
			name: "default true",
			input: `commodity USD
	default true`,
			expected: &Commodity{
				Directive: "commodity",
				Symbol:    "USD",
				Default:   true,
			},
			wantErr: false,
		},
		{
			name: "default false",
			input: `commodity EUR
	default false`,
			expected: &Commodity{
				Directive: "commodity",
				Symbol:    "EUR",
				Default:   false,
			},
			wantErr: false,
		},
		{
			name: "default with invalid value",
			input: `commodity GBP
	default yes`,
			wantErr: true,
		},
		{
			name: "default with all fields",
			input: `commodity BTC
	description "Bitcoin"
	subunit 100000000
	default true`,
			expected: &Commodity{
				Directive:   "commodity",
				Symbol:      "BTC",
				Description: "Bitcoin",
				SubUnit:     100000000,
				Default:     true,
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			doc, err := Parse(tt.input, "test.luca")
			if tt.wantErr {
				if err == nil {
					t.Errorf("expected error but got none")
				}
				return
			}
			if err != nil {
				t.Errorf("unexpected error: %v", err)
				return
			}

			if len(doc.Commodities) != 1 {
				t.Errorf("expected 1 commodity, got %d", len(doc.Commodities))
				return
			}

			got := doc.Commodities[0]
			if got.Symbol != tt.expected.Symbol {
				t.Errorf("Symbol = %v, want %v", got.Symbol, tt.expected.Symbol)
			}
			if got.Description != tt.expected.Description {
				t.Errorf("Description = %v, want %v", got.Description, tt.expected.Description)
			}
			if got.SubUnit != tt.expected.SubUnit {
				t.Errorf("SubUnit = %v, want %v", got.SubUnit, tt.expected.SubUnit)
			}
			if got.Default != tt.expected.Default {
				t.Errorf("Default = %v, want %v", got.Default, tt.expected.Default)
			}
		})
	}
}
