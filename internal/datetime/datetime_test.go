package datetime

import (
	"fmt"
	"testing"
	"time"

	"github.com/drummonds/luca/internal/assert"
)

func TestOld(t *testing.T) {
	tm, err := time.Parse(time.DateOnly, "0792-01-01")
	if err != nil {
		t.Fail()
	}
	got := LucaDateTimeString(tm)
	assert.Equal(t, got, "792")
}

func TestDate(t *testing.T) {
	tm, err := time.Parse(time.DateOnly, "2025-01-02")
	if err != nil {
		t.Fail()
	}
	got := LucaDateTimeString(tm)
	assert.Equal(t, got, "2025-01-02")
}

func TestDatetime(t *testing.T) {
	tm, err := time.Parse(time.RFC3339, "2025-01-02T00:01:00Z")
	if err != nil {
		t.Fail()
	}
	got := LucaDateTimeString(tm)
	assert.Equal(t, got, "2025-01-02T00:01:00Z")
}

func TestAll(t *testing.T) {
	type testData struct {
		parseFormat string
		parse       string
		want        string
	}
	tdl := []testData{
		{parseFormat: time.RFC3339,
			parse: "2025-01-02T00:01:00+01:00",
			want:  "2025-01-02T00:01:00+01:00"},
		{parseFormat: time.RFC3339Nano,
			parse: "2025-01-02T00:01:00.0000001+01:00",
			want:  "2025-01-02T00:01:00.0000001+01:00"},
		{parseFormat: time.RFC3339,
			parse: "2025-01-02T00:01:00+00:00",
			want:  "2025-01-02T00:01:00Z"},
	}
	for _, td := range tdl {
		tm, err := time.Parse(td.parseFormat, td.parse)
		if err != nil {
			t.Logf(fmt.Sprintf("Failed to parse test data %+v", err))
			t.Fail()
			continue
		}
		got := LucaDateTimeString(tm)
		assert.Equal(t, got, td.want)
	}
}
