package parser

import (
	"testing"
)

func TestGenericParse(t *testing.T) {
	tests := ParserTests{
		{
			name:    "empty entry",
			input:   ``,
			want:    &Document{},
			wantErr: false,
		},
		{
			name: "just a comment which gets ignored as no directive",
			input: `; This is a comment
`,
			expectedInput: new(string),
			want:          &Document{},
			wantErr:       false,
		},
		{
			name: "simplest generic entry",
			input: `2024-01-01 generic
`,
			want: &Document{
				GenericEntries: []*GenericEntry{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive:     "generic",
						Description:   "",
						SubDirectives: nil,
					},
				},
			},
			wantErr: false,
		},
		{
			name: "simplest generic entry with knowledge date",
			input: `2024-01-01 ^2024-01-02 generic
`,
			want: &Document{
				GenericEntries: []*GenericEntry{
					{
						EntryHeader: EntryHeader{
							Date:          ParseDate("2024-01-01"),
							KnowledgeDate: ParseDate("2024-01-02"),
						},
						Directive:     "generic",
						Description:   "",
						SubDirectives: nil,
					},
				},
			},
			wantErr: false,
			debug:   false,
		},
		{
			name: "simplest generic entry with knowledge date and comment",
			input: `2024-01-01 ^2024-01-02 generic ; This is a comment
`,
			want: &Document{
				GenericEntries: []*GenericEntry{
					{
						EntryHeader: EntryHeader{
							Date:          ParseDate("2024-01-01"),
							KnowledgeDate: ParseDate("2024-01-02"),
						},
						Directive:     "generic",
						Description:   "",
						Comment:       "This is a comment",
						SubDirectives: nil,
					},
				},
			},
			wantErr: false,
			debug:   false,
		},
		{
			name: "simplest generic entry with comment",
			input: `; Generic test with comment
2024-01-01 generic
`,
			want: &Document{
				GenericEntries: []*GenericEntry{
					{
						EntryHeader: EntryHeader{
							Date:     ParseDate("2024-01-01"),
							Comments: []string{"Generic test with comment"},
						},
						Directive:     "generic",
						Description:   "",
						SubDirectives: nil,
					},
				},
			},
			wantErr: false,
		},
		{
			name: "simplest generic entry with comment",
			input: `; Generic test with comment
; Second comment
2024-01-01 generic
`,
			want: &Document{
				GenericEntries: []*GenericEntry{
					{
						EntryHeader: EntryHeader{
							Date:     ParseDate("2024-01-01"),
							Comments: []string{"Generic test with comment", "Second comment"},
						},
						Directive:     "generic",
						Description:   "",
						SubDirectives: nil,
					},
				},
			},
			wantErr: false,
		},
		{
			name: "simplest generic entry with description",
			input: `2024-01-01 generic "Grocery shopping"
`,
			want: &Document{
				GenericEntries: []*GenericEntry{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive:     "generic",
						Description:   "Grocery shopping",
						SubDirectives: nil,
					},
				},
			},
			wantErr: false,
		},
		{
			name: "generic entry with subdirective",
			input: `2024-01-01 generic "Grocery shopping"
	"assets:bank -50.00"
`, // Needs to be a single string
			want: &Document{
				GenericEntries: []*GenericEntry{
					{
						EntryHeader: EntryHeader{
							Date: ParseDate("2024-01-01"),
						},
						Directive:   "generic",
						Description: "Grocery shopping",
						SubDirectives: []SubDirective{
							{Text: "assets:bank -50.00"},
						},
					},
				},
			},
			wantErr: false,
		},
	}
	AbstractTestParse(t, tests)
}
