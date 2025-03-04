package parser

// GetTransactions extracts all Transaction entries from a Document
func GetTransactions(doc *Document) []*Transaction {
	var transactions []*Transaction
	for _, entry := range doc.Entries {
		if txn, ok := entry.(*Transaction); ok {
			transactions = append(transactions, txn)
		}
	}
	return transactions
}

// GetAccounts extracts all Account entries from a Document
func GetAccounts(doc *Document) []*Account {
	var accounts []*Account
	for _, entry := range doc.Entries {
		if acc, ok := entry.(*Account); ok {
			accounts = append(accounts, acc)
		}
	}
	return accounts
}

// GetCommodities extracts all Commodity entries from a Document
func GetCommodities(doc *Document) []*Commodity {
	var commodities []*Commodity
	for _, entry := range doc.Entries {
		if comm, ok := entry.(*Commodity); ok {
			commodities = append(commodities, comm)
		}
	}
	return commodities
}
