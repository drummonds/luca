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
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					Description: "US Dollar",
					SubUnit:     100,
				},
			},
			b: Commodity{
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					Description: "US Dollar",
					SubUnit:     100,
				},
			},
			want: true,
		},
		{
			name: "different IDs",
			a: Commodity{
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					Description: "US Dollar",
					SubUnit:     100,
				},
			},
			b: Commodity{
				Directive: "commodity",
				Id:        "EUR",
				CommodityDetail: CommodityDetail{
					Description: "US Dollar",
					SubUnit:     100,
				},
			},
			want: false,
		},
		{
			name: "different descriptions",
			a: Commodity{
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					Description: "US Dollar",
					SubUnit:     100,
				},
			},
			b: Commodity{
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					Description: "United States Dollar",
					SubUnit:     100,
				},
			},
			want: false,
		},
		{
			name: "different subunits",
			a: Commodity{
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					Description: "US Dollar",
					SubUnit:     100,
				},
			},
			b: Commodity{
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					Description: "US Dollar",
					SubUnit:     1000,
				},
			},
			want: false,
		},
		{
			name: "empty details",
			a: Commodity{
				Directive: "commodity",
				Id:        "USD",
			},
			b: Commodity{
				Directive: "commodity",
				Id:        "USD",
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

func TestCommodityDetailEqual(t *testing.T) {
	tests := []struct {
		name string
		a    CommodityDetail
		b    CommodityDetail
		want bool
	}{
		{
			name: "identical details",
			a: CommodityDetail{
				Description: "US Dollar",
				SubUnit:     100,
			},
			b: CommodityDetail{
				Description: "US Dollar",
				SubUnit:     100,
			},
			want: true,
		},
		{
			name: "different descriptions",
			a: CommodityDetail{
				Description: "US Dollar",
				SubUnit:     100,
			},
			b: CommodityDetail{
				Description: "United States Dollar",
				SubUnit:     100,
			},
			want: false,
		},
		{
			name: "different subunits",
			a: CommodityDetail{
				Description: "US Dollar",
				SubUnit:     100,
			},
			b: CommodityDetail{
				Description: "US Dollar",
				SubUnit:     1000,
			},
			want: false,
		},
		{
			name: "empty details",
			a:    CommodityDetail{},
			b:    CommodityDetail{},
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
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					Description: "US Dollar",
					SubUnit:     100,
				},
			},
			want: " commodity USD\n\tdescription \"US Dollar\"\n\tsubunit 100\n",
		},
		{
			name: "commodity without description",
			commodity: Commodity{
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					SubUnit: 100,
				},
			},
			want: " commodity USD\n\tsubunit 100\n",
		},
		{
			name: "commodity without subunit",
			commodity: Commodity{
				Directive: "commodity",
				Id:        "USD",
				CommodityDetail: CommodityDetail{
					Description: "US Dollar",
				},
			},
			want: " commodity USD\n\tdescription \"US Dollar\"\n",
		},
		{
			name: "minimal commodity",
			commodity: Commodity{
				Directive: "commodity",
				Id:        "USD",
			},
			want: " commodity USD\n",
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

func TestCommodityDetailToStringBuilder(t *testing.T) {
	tests := []struct {
		name   string
		detail CommodityDetail
		want   string
	}{
		{
			name: "full detail",
			detail: CommodityDetail{
				Description: "US Dollar",
				SubUnit:     100,
			},
			want: "\tdescription \"US Dollar\"\n\tsubunit 100\n",
		},
		{
			name: "detail without description",
			detail: CommodityDetail{
				SubUnit: 100,
			},
			want: "\tsubunit 100\n",
		},
		{
			name: "detail without subunit",
			detail: CommodityDetail{
				Description: "US Dollar",
			},
			want: "\tdescription \"US Dollar\"\n",
		},
		{
			name:   "empty detail",
			detail: CommodityDetail{},
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

func TestParseCommodity(t *testing.T) {
	tests := ParserTests{
		{
			name: "basic commodity",
			input: `2024-01-01 commodity USD
	description "US Dollar"
	subunit 100
`,
			want: &Document{
				Entries: []*Entry{
					{
						Date: "2024-01-01",
						Commodity: &Commodity{
							Directive: "commodity",
							Id:        "USD",
							CommodityDetail: CommodityDetail{
								Description: "US Dollar",
								SubUnit:     100,
							},
						},
					},
				},
			},
			wantErr: false,
		},
		{
			name: "commodity without description",
			input: `2024-01-01 commodity USD
	subunit 100
`,
			want: &Document{
				Entries: []*Entry{
					{
						Date: "2024-01-01",
						Commodity: &Commodity{
							Directive: "commodity",
							Id:        "USD",
							CommodityDetail: CommodityDetail{
								SubUnit: 100,
							},
						},
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
				Entries: []*Entry{
					{
						Date: "2024-01-01",
						Commodity: &Commodity{
							Directive: "commodity",
							Id:        "USD",
							CommodityDetail: CommodityDetail{
								Description: "US Dollar",
							},
						},
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
				Entries: []*Entry{
					{
						Date: "2024-01-01",
						Commodity: &Commodity{
							Directive: "commodity",
							Id:        "USD",
						},
					},
				},
			},
			wantErr: false,
		},
	}
	AbstractTestParse(t, tests)
}
