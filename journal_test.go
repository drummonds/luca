package luca

import (
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/spf13/afero"
	"github.com/stretchr/testify/assert"
)

type testJournal struct {
	name     string
	content  string
	expected []Entry
	wantErr  bool
}

func getSingleEntry() (content string, expected Entry) {
	content = `2024-01-01 directive param1 param2 //comment
    arg1 //arg comment
    arg2`
	expected = Entry{
		Lines: []string{
			"2024-01-01 directive param1 param2 //comment",
			"    arg1 //arg comment",
			"    arg2",
		},
		ThisDirective: DirectiveHeader{
			ValueDate:   time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
			Name:        "directive",
			ExtraParams: "param1 param2",
			Comment:     "comment",
		},
		Arguments: []RawArgument{
			{Value: "arg1", Comment: "arg comment"},
			{Value: "arg2", Comment: ""},
		},
	}
	return
}

func getSimpleEntry(directive string) (content string, expected Entry) {
	return getSimpleWithCommentsEntry(directive, 0)
}

func getSimpleWithCommentsEntry(directive string, numComments int) (content string, expected Entry) {
	var (
		sb    strings.Builder
		lines []string
		s     string
	)
	for i := 0; i < numComments; i++ {
		s = fmt.Sprintf("# comment %d", i)
		sb.WriteString(s)
		sb.WriteString("\n")
		lines = append(lines, s)
	}
	s = fmt.Sprintf("2024-01-01 %s param1 param2 //comment", directive)
	sb.WriteString(s)
	sb.WriteString("\n")
	lines = append(lines, s)
	s = "    arg"
	sb.WriteString(s)
	sb.WriteString("\n")
	lines = append(lines, s)
	content = sb.String()

	expected = Entry{
		Lines: lines,
		ThisDirective: DirectiveHeader{
			ValueDate:   time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC),
			Name:        directive,
			ExtraParams: "param1 param2",
			Comment:     "comment",
		},
		Arguments: []RawArgument{
			{Value: "arg", Comment: ""},
		},
		Comments: lines[:numComments],
	}
	return
}

func getSingleEntryJournal() testJournal {
	content, entry := getSingleEntry()
	test := testJournal{
		name:     "single entry",
		content:  content,
		expected: []Entry{entry},
	}
	return test
}

func getEmptyEntryJournal() testJournal {
	test := testJournal{
		name:     "No entries",
		content:  "",
		expected: []Entry{},
	}
	return test
}

func getMultipleEntries() testJournal {
	var sb strings.Builder
	c1, e1 := getSimpleEntry("first")
	c2, e2 := getSimpleEntry("second")

	sb.WriteString(c1)
	sb.WriteString("\n\n")
	sb.WriteString(c2)

	test := testJournal{
		name:     "multiple entries with empty lines",
		content:  sb.String(),
		expected: []Entry{e1, e2},
	}
	return test
}

func getMultipleEntriesWithComments() testJournal {
	var sb strings.Builder
	c1, e1 := getSimpleWithCommentsEntry("first", 0)
	c2, e2 := getSimpleWithCommentsEntry("second", 1)
	c3, e3 := getSimpleWithCommentsEntry("second", 2)

	sb.WriteString(c1)
	sb.WriteString(c2)
	sb.WriteString("\n\n")
	sb.WriteString(c3)

	test := testJournal{
		name:     "multiple entries with empty lines",
		content:  sb.String(),
		expected: []Entry{e1, e2, e3},
	}
	return test
}

func TestProduceEntries(t *testing.T) {
	tests := []testJournal{
		getSingleEntryJournal(),
		// getMultipleEntries(),
		// getMultipleEntriesWithComments(),
		// getEmptyEntryJournal(),
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Setup in-memory filesystem
			fs := afero.NewMemMapFs()
			filename := "test.journal"
			err := afero.WriteFile(fs, filename, []byte(tt.content), 0644)
			assert.NoError(t, err)

			// Create channel and collect entries
			entryChan := make(chan Entry)
			entries := []Entry{}

			// Start producer in goroutine
			errChan := make(chan error, 1)
			go func() {
				defer close(entryChan)
				if err := ProduceEntries(fs, filename, entryChan); err != nil {
					errChan <- err
				}
			}()

			// Collect entries
			for entry := range entryChan {
				entries = append(entries, entry)
			}

			// Check for errors
			select {
			case err := <-errChan:
				if !tt.wantErr {
					t.Errorf("unexpected error: %v", err)
				}
			default:
				if tt.wantErr {
					t.Error("expected error but got none")
				}
			}

			// Compare results
			assert.Equal(t, tt.expected, entries)
		})
	}

	t.Run("file not found", func(t *testing.T) {
		fs := afero.NewMemMapFs()
		entryChan := make(chan Entry)
		err := ProduceEntries(fs, "nonexistent.journal", entryChan)
		assert.Error(t, err)
	})
}
