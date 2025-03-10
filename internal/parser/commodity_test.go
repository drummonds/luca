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
