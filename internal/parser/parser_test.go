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

func TestParse(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		want    *Document
		wantErr bool
	}{
		{
			name:  "empty entry",
			input: ``,
			want: &Document{
				Entries: nil,
			},
			wantErr: false,
		},
		{
			name:  "simplest generic entry",
			input: `2024-01-01 generic`,
			want: &Document{
				Entries: []*Entry{
					{
						Date: "2024-01-01",
						Generic: &GenericEntry{
							Directive:     "generic",
							Description:   "",
							SubDirectives: nil,
						},
					},
				},
			},
			wantErr: false,
		},
		{
			name:  "simplest generic entry with description",
			input: `2024-01-01 generic "Grocery shopping"`,
			want: &Document{
				Entries: []*Entry{
					{
						Date: "2024-01-01",
						Generic: &GenericEntry{
							Directive:     "generic",
							Description:   "Grocery shopping",
							SubDirectives: nil,
						},
					},
				},
			},
			wantErr: false,
		},
		{
			name: "basic generic entry",
			input: `2024-01-01 generic "Grocery shopping"
    "assets:bank -50.00"`, // Needs to be a single string
			want: &Document{
				Entries: []*Entry{
					{
						Date: "2024-01-01",
						Generic: &GenericEntry{
							Directive:   "generic",
							Description: `"Grocery shopping"`,
							SubDirectives: []SubDirective{
								{Text: "assets:bank-50.00"},
							},
						},
					},
				},
			},
			wantErr: false,
		},
		{
			name: "basic transaction",
			input: `2024-01-01 txn "Coffee shop"
    "food  3.50 -> assets:cash`,
			want: &Document{
				Entries: []*Entry{
					{
						Date: "2024-01-01",
						Transaction: &Transaction{
							Directive:   "txn",
							Description: `"Coffee shop"`,
							Movements: []Movement{
								{From: "expenses:food", To: "assets:cash", Amount: "3.50"},
							},
						},
					},
				},
			},
			wantErr: false,
		},
	}

	for i, tt := range tests {
		if i > 2 {
			continue
		}
		t.Run(tt.name, func(t *testing.T) {
			got, err := Parse(tt.input)
			// got, err := ParseWithDebug(tt.input)
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

// documentsEqual compares two Documents for equality
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
		return transactionsEqual(a.Transaction, b.Transaction)
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

// genericEntriesEqual compares two GenericEntries for equality
func genericEntriesEqual(a, b *GenericEntry) bool {
	if a.Directive != b.Directive || a.Description != b.Description {
		return false
	}
	return ArrayEqual(a.SubDirectives, b.SubDirectives)
}

// transactionsEqual compares two Transactions for equality
func transactionsEqual(a, b *Transaction) bool {
	if a.Directive != b.Directive || a.Description != b.Description {
		return false
	}
	return ArrayEqual(a.Movements, b.Movements)
}
