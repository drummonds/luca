package mermaid

import (
	"fmt"
	"strings"

	"github.com/shopspring/decimal"
)

type Node struct {
	ID       string
	Label    string
	Balance  decimal.Decimal
	Class    string
	Currency string
}

func GenerateMermaidSummary(nodes []Node, edges []Edge) string {
	var sb strings.Builder

	// Start flowchart
	sb.WriteString("flowchart LR\n")

	// Add class definitions
	sb.WriteString("classDef classAssets fill:#CDA;\n")
	sb.WriteString("classDef classBusiness fill:#FFFFDE;\n")
	sb.WriteString("classDef classEquity fill:#EEB,stroke-width:4px;\n")
	sb.WriteString("classDef classExpense fill:#FCC,stroke-width:4px;\n")
	sb.WriteString("classDef classIncome fill:#BCE,stroke-width:4px;\n")
	sb.WriteString("classDef classLiabilities fill:#DDD;\n")

	// Add nodes
	for _, node := range nodes {
		sb.WriteString(fmt.Sprintf("%s([%s **%s%s**])\n",
			node.ID,
			node.Label,
			node.Currency,
			node.Balance.StringFixed(2)))
		sb.WriteString(fmt.Sprintf("class %s %s;\n", node.ID, node.Class))
	}

	// Add subgraph for internal nodes
	// TODO Need algorithm to sort external and internal nodes
	sb.WriteString("subgraph Internal\n")
	sb.WriteString("  direction LR\n")
	// Add internal nodes here
	sb.WriteString("end\n")

	// Add edges
	for _, edge := range edges {
		sb.WriteString(fmt.Sprintf("%s -- %s%s --> %s\n",
			edge.From,
			edge.Currency,
			edge.Amount.StringFixed(2),
			edge.To))
	}

	return sb.String()
}

type Edge struct {
	From     string
	To       string
	Amount   decimal.Decimal
	Currency string
}
