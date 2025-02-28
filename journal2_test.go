package luca

import (
	"testing"

	"github.com/spf13/afero"
)

// Mock handlers for testing
type mockHandler struct {
	directiveName string
	processed     [][]string
}

func (h *mockHandler) HandleEntry(entry Entry) bool {
	if entry.ThisDirective.Name == h.directiveName {
		h.processed = append(h.processed, entry.Lines)
		return true
	}
	return false
}

func TestReadJournalEntries(t *testing.T) {
	// Create a memory-backed filesystem
	fs := afero.NewMemMapFs()

	content := `2024-01-01 first entry line 1
  First entry line 2

2024-01-02 second entry line 1
  Second entry line 2
# This is a comment

2024-01-03 third entry line 1
 Third entry line 2`

	// Write test file to memory filesystem
	if err := afero.WriteFile(fs, "test.txt", []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	// Create mock handlers
	firstHandler := &mockHandler{directiveName: "first"}
	secondHandler := &mockHandler{directiveName: "second"}
	thirdHandler := &mockHandler{directiveName: "third"}

	handlers := []EntryHandler{firstHandler, secondHandler, thirdHandler}

	// Test the function with the memory filesystem
	err := ReadJournalEntries(fs, "test.txt", handlers)
	if err != nil {
		t.Fatalf("ReadJournalEntries() error = %v", err)
	}

	// Verify handlers processed correct entries
	if len(firstHandler.processed) != 1 {
		t.Errorf("First handler processed %d entries, want 1", len(firstHandler.processed))
	}
	if len(secondHandler.processed) != 1 {
		t.Errorf("Second handler processed %d entries, want 1", len(secondHandler.processed))
	}
	if len(thirdHandler.processed) != 1 {
		t.Errorf("Third handler processed %d entries, want 1", len(thirdHandler.processed))
	}
}

func TestReadJournalEntriesUnhandledEntry(t *testing.T) {
	fs := afero.NewMemMapFs()

	content := `1999 first entry line 1
  First entry line 2
2000 Unhandled entry line 1
  Unhandled entry line 2`

	if err := afero.WriteFile(fs, "test.txt", []byte(content), 0644); err != nil {
		t.Fatal(err)
	}

	// Create mock handler that only handles "First" entries
	handler := &mockHandler{directiveName: "first"}
	handlers := []EntryHandler{handler}

	// Test the function with the memory filesystem
	err := ReadJournalEntries(fs, "test.txt", handlers)
	if err == nil {
		t.Error("ReadJournalEntries() expected error for unhandled entry, got nil")
	}
}

func TestReadJournalEntriesErrors(t *testing.T) {
	fs := afero.NewMemMapFs()
	// Test with non-existent file
	err := ReadJournalEntries(fs, "nonexistent_file.txt", []EntryHandler{})
	if err == nil {
		t.Error("ReadJournalEntries() expected error for non-existent file, got nil")
	}
}
