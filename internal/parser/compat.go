package parser

// EntryToTransaction converts an old-style Entry to a Transaction
func EntryToTransaction(e *Entry) *Transaction {
	return &Transaction{
		EntryDate: EntryDate{
			Date:          e.Date,
			KnowledgeDate: e.KnowledgeDate,
			Comments:      e.Comments,
		},
		Type:           e.Type,
		Payee:          e.Payee,
		PostingStrings: e.PostingStrings,
	}
}

// TransactionToEntry converts a Transaction to an old-style Entry
func TransactionToEntry(t *Transaction) *Entry {
	return &Entry{
		Date:           t.Date,
		KnowledgeDate:  t.KnowledgeDate,
		Type:           t.Type,
		Payee:          t.Payee,
		PostingStrings: t.PostingStrings,
		Comments:       t.Comments,
	}
}

// AccountToEntry converts an Account to an old-style Entry
func AccountToEntry(a *Account) *Entry {
	return &Entry{
		Date:          a.Date,
		KnowledgeDate: a.KnowledgeDate,
		Type:          a.Type,
		Account:       a.Name,
		Comments:      a.Comments,
	}
}

// CommodityToEntry converts a Commodity to an old-style Entry
func CommodityToEntry(c *Commodity) *Entry {
	return &Entry{
		Date:          c.Date,
		KnowledgeDate: c.KnowledgeDate,
		Type:          c.Type,
		Commodity:     c.Name,
		Comments:      c.Comments,
	}
}
