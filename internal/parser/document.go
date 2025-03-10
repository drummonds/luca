package parser

import (
	"strings"
)

// Document represents a complete financial document with multiple entries
type Document struct {
	// Entries contains all entries in the document
	// However they are in strongly typed lists
	Commodities    []*Commodity
	Accounts       []*Account
	Transactions   []*Transaction
	GenericEntries []*GenericEntry
}

func (d Document) ToStringBuilder(sb *strings.Builder) {
	for _, entry := range d.Commodities {
		entry.ToStringBuilder(sb)
	}
	for _, entry := range d.Accounts {
		entry.ToStringBuilder(sb)
	}
	for _, entry := range d.Transactions {
		entry.ToStringBuilder(sb)
	}
	for _, entry := range d.GenericEntries {
		entry.ToStringBuilder(sb)
	}
}

func (d Document) String() string {
	sb := strings.Builder{}
	d.ToStringBuilder(&sb)
	return sb.String()
}

// ToLines converts the document to a slice of strings
func (d *Document) ToLines() []string {
	var lines []string
	lines = strings.Split(d.String(), "\n")
	return lines
}

// GetEntriesByFilename returns all entries from a specific file
func (d *Document) GetEntriesByFilename(filename string) []JournalEntry {
	var entries []JournalEntry
	// for _, entry := range d.Commodities {
	// 	if entry.GetFilename() == filename {
	// 		entries = append(entries, JournalEntry(entry))
	// 	}
	// }
	// for _, entry := range d.Accounts {
	// 	entry.ToStringBuilder(sb)
	// }
	// for _, entry := range d.Transactions {
	// 	entry.ToStringBuilder(sb)
	// }
	// for _, entry := range d.GenericEntries {
	// 	entry.ToStringBuilder(sb)
	// }
	// for _, entry := range d.Entries {
	// 	if entry.GetFilename() == filename {
	// 		entries = append(entries, entry)
	// 	}
	// }
	return entries
}

// GetUniqueFilenames returns a list of all unique filenames in the document
func (d *Document) GetUniqueFilenames() []string {
	fileMap := make(map[string]bool)
	// for _, entry := range d.Entries {
	// 	filename := entry.GetFilename()
	// 	if filename != "" {
	// 		fileMap[filename] = true
	// 	}
	// }

	var filenames []string
	for filename := range fileMap {
		filenames = append(filenames, filename)
	}
	return filenames
}

// GetTransactions extracts all Transaction entries from the Document
func (d *Document) GetTransactions() []*Transaction {
	var transactions []*Transaction
	// for _, entry := range d.Entries {
	// 	if txn, ok := entry.(*Transaction); ok {
	// 		transactions = append(transactions, txn)
	// 	}
	// }
	return transactions
}

// Similar methods for other types...
