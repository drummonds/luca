package luca

import (
	"io"
	"strings"
	"testing"
	"time"

	"github.com/drummonds/luca/internal/assert"
)

func TestWrite(t *testing.T) {
	c := Commodity{ Comments:{"This for GBP"},
	ValueDate: time.Parse(time.DateOnly,"892-01-01"),
	Id: "GBP",
	Name: "Pound sterling",
	SubUnit: 100,
	}
	var writer io.WriteString
    var buf strings.Builder // Use strings.Builder for efficiency
                // Write to string buffer
                writer = &buf
  
        _, err := io.WriteString(&buf, text) // Or io.WriteString(&sb, text) for strings.Builder

        if err != nil {
                return "", fmt.Errorf("error writing to buffer: %w", err)
        }

        // Convert the buffer's contents to a string.
        return buf.String(), nil // Or sb.String() for strings.Builder
}

func main() {
        text := "Hello, world! This is some text written to a buffer."

        result, err := writeToStringBuffer(text)
        if err != nil {
                fmt.Println("Error:", err)
                os.Exit(1)
        }

        fmt.Println("Text written to buffer:", result)

    // Example of writing to os.Stdout (also an io.Writer)
    _, err = io.WriteString(os.Stdout, "This is written directly to stdout\n")
    if err != nil {
        fmt.Println("Error writing to stdout:", err)
    }


}

	s := c.Write()

892-01-01 commodity GBP

	description "Pound sterling"
	sub-unit 100}

}


// func Test_ParseCommodity(t *testing.T) {
// 	r := strings.NewReader(`
// commodity NBC814
//   note Altamira Precision Canadian Index Fund
//   format 1.0000 NBC814

// commodity BND
//   note Vanguard Total Bond Market ETF
//   format 1 BND
// `)
// 	p := NewParser(r)
// 	i, err := p.Next("")
// 	assert.NoError(t, err)
// 	c, ok := i.(*Commodity)
// 	assert.Equal(t, ok, true)
// 	assert.Equal(t, c.Id, "NBC814")
// 	assert.Equal(t, c.Name, "Altamira Precision Canadian Index Fund")
// 	assert.Equal(t, c.Decimals, 4)

// 	i, err = p.Next("")
// 	assert.NoError(t, err)
// 	c, ok = i.(*Commodity)
// 	assert.Equal(t, ok, true)
// 	assert.Equal(t, c.Id, "BND")
// 	assert.Equal(t, c.Name, "Vanguard Total Bond Market ETF")
// 	assert.Equal(t, c.Decimals, 0)
// }
