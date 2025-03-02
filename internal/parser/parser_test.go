package parser

import (
	"testing"

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
				got, err = Parse(tt.input)
			}
			if (err != nil) != tt.wantErr {
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
