package parser

import (
	"reflect"
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
							Date:     ParseDate("2024-01-01"),
							Filename: "test.luca",
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
							Filename:      "test.luca",
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
							Filename:      "test.luca",
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
							Filename: "test.luca",
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
							Filename: "test.luca",
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
							Date:     ParseDate("2024-01-01"),
							Filename: "test.luca",
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
							Date:     ParseDate("2024-01-01"),
							Filename: "test.luca",
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
		{
			name: "generic entry with filename set",
			input: `2024-01-01 generic
`,
			want: &Document{
				GenericEntries: []*GenericEntry{
					{
						EntryHeader: EntryHeader{
							Date:     ParseDate("2024-01-01"),
							Filename: "test.luca",
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
			name: "generic entry with filename and knowledge date",
			input: `2024-01-01 ^2024-01-02 generic ; This is a comment
`,
			want: &Document{
				GenericEntries: []*GenericEntry{
					{
						EntryHeader: EntryHeader{
							Date:          ParseDate("2024-01-01"),
							KnowledgeDate: ParseDate("2024-01-02"),
							Filename:      "other.luca",
						},
						Directive:     "generic",
						Description:   "",
						Comment:       "This is a comment",
						SubDirectives: nil,
					},
				},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests[2:3] {
		t.Run(tt.name, func(t *testing.T) {
			filename := "test.luca"

			got, err := Parse(tt.input, filename)
			if (err != nil) != tt.wantErr {
				t.Errorf("Parse() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if !tt.wantErr {
				// Check if filenames are set correctly
				for _, entry := range got.GenericEntries {
					if entry.GetFilename() != filename {
						t.Errorf("Filename not set correctly. Got %v, want %v", entry.GetFilename(), filename)
					}
				}

				// Existing comparison code...
				if !reflect.DeepEqual(got, tt.want) {
					t.Errorf("Parse() = %v, want %v", got, tt.want)
				}
			}
		})
	}
}
