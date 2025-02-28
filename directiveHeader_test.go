package luca

import (
	"testing"
	"time"
)

func testdirectiveHeaderString(t *testing.T) {
	kd := time.Date(2024, 3, 16, 0, 0, 0, 0, time.UTC)
	tests := []struct {
		name     string
		header   DirectiveHeader
		expected string
	}{
		// {
		// 	name: "basic directive without knowledge date",
		// 	header: DirectiveHeader{
		// 		ValueDate: time.Date(2024, 3, 15, 0, 0, 0, 0, time.UTC),
		// 		Name:      "testdirective",
		// 		Comment:   "",
		// 	},
		// 	expected: "2024-03-15 testdirective\n",
		// },
		{
			name: "directive with comment",
			header: DirectiveHeader{
				ValueDate: time.Date(2024, 3, 15, 0, 0, 0, 0, time.UTC),
				Name:      "testdirective",
				Comment:   "This is a test",
			},
			expected: "2024-03-15 testdirective // This is a test\n",
		},
		{
			name: "directive with knowledge date",
			header: DirectiveHeader{
				ValueDate:     time.Date(2024, 3, 15, 0, 0, 0, 0, time.UTC),
				KnowledgeDate: &kd,
				Name:          "testdirective",
				Comment:       "",
			},
			expected: "2024-03-15 ^2024-03-16 testdirective\n",
		},
		{
			name: "directive with extra params",
			header: DirectiveHeader{
				ValueDate:   time.Date(2024, 3, 15, 0, 0, 0, 0, time.UTC),
				Name:        "testdirective",
				ExtraParams: "param1 param2",
				Comment:     "",
			},
			expected: "2024-03-15 testdirective param1 param2\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := tt.header.String()
			if result != tt.expected {
				t.Errorf("String() = %v, want %v", result, tt.expected)
			}
		})
	}
}

func TestNewDirectiveHeader(t *testing.T) {
	tests := []struct {
		name        string
		input       string
		wantErr     bool
		expectedDir DirectiveHeader
	}{
		{
			name:    "basic directive",
			input:   "2024-03-15 testdirective",
			wantErr: false,
			expectedDir: DirectiveHeader{
				ValueDate: time.Date(2024, 3, 15, 0, 0, 0, 0, time.UTC),
				Name:      "testdirective",
			},
		},
		{
			name:    "directive with comment",
			input:   "2024-03-15 testdirective // This is a test",
			wantErr: false,
			expectedDir: DirectiveHeader{
				ValueDate: time.Date(2024, 3, 15, 0, 0, 0, 0, time.UTC),
				Name:      "testdirective",
				Comment:   "This is a test",
			},
		},
		{
			name:    "invalid date format",
			input:   "invalid-date testdirective",
			wantErr: true,
		},
		{
			name:    "empty line",
			input:   "",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			directive, err := NewDirectiveHeader(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("NewDirectiveHeader() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				if !directive.ValueDate.Equal(tt.expectedDir.ValueDate) {
					t.Errorf("ValueDate = %v, want %v", directive.ValueDate, tt.expectedDir.ValueDate)
				}
				if directive.Name != tt.expectedDir.Name {
					t.Errorf("Name = %v, want %v", directive.Name, tt.expectedDir.Name)
				}
				if directive.Comment != tt.expectedDir.Comment {
					t.Errorf("Comment = %v, want %v", directive.Comment, tt.expectedDir.Comment)
				}
			}
		})
	}
}

func testdirectiveHeaderRoundTrip(t *testing.T) {
	kd := time.Date(2024, 3, 16, 0, 0, 0, 0, time.UTC)
	originalHeaders := []DirectiveHeader{
		{
			ValueDate: time.Date(2024, 3, 15, 0, 0, 0, 0, time.UTC),
			Name:      "testdirective",
			Comment:   "Test comment",
		},
		{
			ValueDate:     time.Date(2024, 3, 15, 0, 0, 0, 0, time.UTC),
			KnowledgeDate: &kd,
			Name:          "testdirective",
			ExtraParams:   "param1 param2",
			Comment:       "Test with knowledge date",
		},
	}

	for i, original := range originalHeaders {
		// Convert to string
		str := original.String()

		// Parse back to DirectiveHeader
		parsed, err := NewDirectiveHeader(str)
		if err != nil {
			t.Errorf("Test case %d: Failed to parse string back to DirectiveHeader: %v", i, err)
			continue
		}

		// Compare fields
		if !parsed.ValueDate.Equal(original.ValueDate) {
			t.Errorf("Test case %d: ValueDate mismatch: got %v, want %v", i, parsed.ValueDate, original.ValueDate)
		}
		if parsed.Name != original.Name {
			t.Errorf("Test case %d: Name mismatch: got %v, want %v", i, parsed.Name, original.Name)
		}
		if parsed.Comment != original.Comment {
			t.Errorf("Test case %d: Comment mismatch: got %v, want %v", i, parsed.Comment, original.Comment)
		}
	}
}
