package luca

import (
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestWrite(t *testing.T) {
	// Create test commodity
	c := Commodity{
		Comments:  []string{"This for GBP"},
		ValueDate: time.Date(892, 1, 1, 0, 0, 0, 0, time.UTC),
		Id:        "GBP",
		Name:      "Pound sterling",
		SubUnit:   100,
	}

	// Create a strings.Builder which implements io.Writer
	var buf strings.Builder

	// Write commodity data to the buffer
	err := c.Write(&buf)
	assert.NoError(t, err)

	expected := `892-01-01 commodity GBP
	description "Pound sterling"
	sub-unit 100`

	assert.Equal(t, strings.TrimSpace(expected), strings.TrimSpace(buf.String()))
}
