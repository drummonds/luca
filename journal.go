package luca

import (
	"bufio"
	"fmt"
	"strings"
	"unicode"

	"github.com/spf13/afero"
)

// Entry represents a parsed journal entry
type Entry struct {
	Lines         []string // Original lines for backwards compatibility
	Comments      []string
	ThisDirective DirectiveHeader
	Arguments     []RawArgument
}

func NewEntry() Entry {
	return Entry{
		Lines:         []string{},
		Comments:      []string{},
		ThisDirective: DirectiveHeader{},
		Arguments:     []RawArgument{},
	}
}

func (e *Entry) HasDirective() bool {
	return e.ThisDirective.Name != ""
}

// Argument represents a parsed argument line from an entry
type RawArgument struct {
	Value   string
	Comment string
}

// EntryHandler defines the interface for processing journal entries
type EntryHandler interface {
	// HandleEntry attempts to process an entry. Returns true if the entry
	// was successfully handled, false if the entry was not recognized
	HandleEntry(Entry) bool
}

// ReadJournalEntries reads entries from a journal file and processes them using the provided handlers
func ReadJournalEntries(fs afero.Fs, filename string, handlers []EntryHandler) error {
	entryChan := make(chan Entry)
	errChan := make(chan error, 1)

	// Start goroutine to read and produce entries
	go func() {
		defer close(entryChan)
		if err := ProduceEntries(fs, filename, entryChan); err != nil {
			errChan <- err
		}
	}()

	// Process entries as they come in
	if err := processEntries(entryChan, handlers); err != nil {
		return err
	}

	// Check if there was an error during production
	select {
	case err := <-errChan:
		return err
	default:
		return nil
	}
}

// ProduceEntries reads a journal file and sends entries through the provided channel.
// It skips empty lines and adds comments to the entry.  It handles comments both
// for whole lines and for directives and argumentss.
// The caller is responsible for closing the provided channel.
func ProduceEntries(fs afero.Fs, filename string, entryChan chan<- Entry) error {
	file, err := fs.Open(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var (
		entry Entry
	)

	resetEntry := func() {
		entryChan <- entry
		entry = NewEntry()
	}

	for scanner.Scan() {
		line := scanner.Text()
		trimmed := strings.TrimSpace(line)
		switch {
		case trimmed == "" && entry.HasDirective():
			resetEntry()
		case strings.HasPrefix(trimmed, "//"): // Comment
			entry.Comments = append(entry.Comments, strings.TrimSpace(strings.TrimPrefix(trimmed, "//")))
		case trimmed == "": // Skip whitespace between lines
			continue
		case unicode.IsDigit(rune(line[0])): // New directive entry
			if entry.HasDirective() {
				resetEntry()
			}
			entry.Lines = append(entry.Lines, line)
			entry.ThisDirective, err = NewDirectiveHeader(line)
			if err != nil {
				return fmt.Errorf("error parsing directive %s: %+v", line, err)
			}
		default: // Must be an argument
			entry.Lines = append(entry.Lines, line)
			arg, err := NewRawArgument(line)
			if err != nil {
				return fmt.Errorf("error parsing argument %s: %+v", line, err)
			}
			entry.Arguments = append(entry.Arguments, arg)
		}
	}
	// Process the last entry if there are remaining lines
	if entry.HasDirective() {
		resetEntry()
	}
	return scanner.Err()
}

// processEntries processes journal entries using the provided handlers
func processEntries(entryChan <-chan Entry, handlers []EntryHandler) error {
	for entry := range entryChan {
		handled := false
		for _, handler := range handlers {
			if handler.HandleEntry(entry) {
				handled = true
				break
			}
		}

		if !handled {
			return fmt.Errorf("no handler found for entry: %v", entry)
		}
	}

	return nil
}

// processEntry attempts to process an entry with the available handlers
func processEntry(entry Entry, handlers []EntryHandler, filepath string, lineNum int) error {
	for _, handler := range handlers {
		if handler.HandleEntry(entry) {
			return nil
		}
	}

	// If we get here, no handler recognized the entry
	return fmt.Errorf("no handler recognized entry starting at %s:%d:\n%s",
		filepath, lineNum, strings.Join(entry.Lines, "\n"))
}

func NewRawArgument(line string) (argument RawArgument, err error) {
	argument.Value, argument.Comment = SplitComment(line)
	return
}
