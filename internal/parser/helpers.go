package parser

// MergeDocuments combines multiple documents into one
func MergeDocuments(docs ...*Document) *Document {
	merged := &Document{}
	for _, doc := range docs {
		merged.Transactions = append(merged.Transactions, doc.Transactions...)
		merged.Accounts = append(merged.Accounts, doc.Accounts...)
		merged.Commodities = append(merged.Commodities, doc.Commodities...)
	}
	return merged
}
