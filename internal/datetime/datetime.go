package datetime

import (
	"fmt"
	"strings"
	"time"
)

// Make simplest date time strings
// Mostly RFC-3339 but aim to make small as possible
//
//	Start of year make just an integer
//
// If time is zero then just display date
// If second fractions is zero then elide date time
// If nanoseconds is zero then elide
func LucaDateTimeString(t time.Time) string {
	h, m, s := t.Clock()
	midnight := h == 0 && m == 0 && s == 0
	zeroSeconds := t.Nanosecond() == 0
	mon := t.Month()
	day := t.Day()
	location := t.Location()
	isUTC := location.String() == "" || location.String() == "UTC"
	switch {
	// start of year
	case mon == 1 && day == 1 && midnight && zeroSeconds:
		return fmt.Sprintf("%d", t.Year())
	// date
	case midnight && zeroSeconds:
		return t.Format(time.DateOnly)
	case zeroSeconds && isUTC:
		s := t.Format(time.RFC3339)
		if strings.HasSuffix(strings.ToUpper(s), "+00:00") {
			return s[:len(s)-6] + "Z"
		}
		return s
	case zeroSeconds:
		return t.Format(time.RFC3339)
	}
	return t.Format(time.RFC3339Nano)
}
