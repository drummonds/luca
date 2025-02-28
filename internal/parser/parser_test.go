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
	name    string
	input   string
	want    *Document
	wantErr bool
	debug   bool
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
		})
	}
}

func documentsEqual(a, b *Document) bool {
	if len(a.Entries) != len(b.Entries) {
		return false
	}

	for i, entry := range a.Entries {
		if !entriesEqual(entry, b.Entries[i]) {
			return false
		}
	}
	return true
}

// entriesEqual compares two Entries for equality
func entriesEqual(a, b *Entry) bool {
	if a.Date != b.Date {
		return false
	}

	// Compare Generic entries
	if a.Generic != nil && b.Generic != nil {
		return genericEntriesEqual(a.Generic, b.Generic)
	}

	// Compare Transaction entries
	if a.Transaction != nil && b.Transaction != nil {
		return a.Transaction.Equal(b.Transaction)
	}

	// One is nil while the other isn't
	if (a.Generic == nil) != (b.Generic == nil) {
		return false
	}
	if (a.Transaction == nil) != (b.Transaction == nil) {
		return false
	}

	return true
}
