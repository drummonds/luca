package luca

import (
	"time"
)

type Directive interface {
	GetValueDate() time.Time
	GetKnowledgeDate() *time.Time
	GetName() string
	GetExtraParams() string // parsing will be specific to each directive
	GetComment() string
}
