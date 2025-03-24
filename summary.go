package luca

import (
	"strings"

	"github.com/drummonds/luca/internal/mermaid"
)

func (l *Ledger) MermaidSummary() string {
	var nodes []mermaid.Node
	var edges []mermaid.Edge

	// Convert ledger entries to nodes and edges
	for _, account := range l.Accounts {
		nodeClass := "classBusiness" // default
		rootName := strings.ToLower(strings.Split(account.Name, ":")[0])
		switch {
		case strings.HasPrefix(rootName, "assets"):
			nodeClass = "classAssets"
		case strings.HasPrefix(rootName, "equity"):
			nodeClass = "classEquity"
		case strings.HasPrefix(rootName, "expenses"):
			nodeClass = "classExpense"
		case strings.HasPrefix(rootName, "income"):
			nodeClass = "classIncome"
		case strings.HasPrefix(rootName, "liabilities"):
			nodeClass = "classLiabilities"
		}

		nodes = append(nodes, mermaid.Node{
			ID:       strings.Replace(account.Name, ":", "_", -1),
			Label:    account.Name,
			Balance:  account.BalanceLatest(),
			Class:    nodeClass,
			Currency: "£", // You might want to make this configurable
		})
	}

	// Add edges from transactions
	for _, tx := range l.Transactions {
		// Convert transactions to edges
		for _, m := range tx.Movements {
			edges = append(edges, mermaid.Edge{
				From:     strings.Replace(m.From, ":", "_", -1),
				To:       strings.Replace(m.To, ":", "_", -1),
				Amount:   m.Amount,
				Currency: "£", //TODO
			})
		}
	}

	return mermaid.GenerateMermaidSummary(nodes, edges)
}
