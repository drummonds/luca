package datetime

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestOld(t *testing.T) {
	tm, err := time.Parse(time.DateOnly, "0792-01-01")
	if err != nil {
		t.Fail()
	}
	got := LucaDateTimeString(tm)
	assert.Equal(t, "792", got)
}

func TestDate(t *testing.T) {
	tm, err := time.Parse(time.DateOnly, "2025-01-02")
	if err != nil {
		t.Fail()
	}
	got := LucaDateTimeString(tm)
	assert.Equal(t, "2025-01-02", got)
}

func TestDatetime(t *testing.T) {
	tm, err := time.Parse(time.RFC3339, "2025-01-02T00:01:00Z")
	if err != nil {
		t.Fail()
	}
	got := LucaDateTimeString(tm)
	assert.Equal(t, "2025-01-02T00:01:00Z", got)
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
		assert.Equal(t, td.want, got)
	}
}

func TestParseLucaDateTime(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		want    time.Time
		wantErr bool
	}{
		{
			name:    "simple date",
			input:   "2025-01-02",
			want:    time.Date(2025, 1, 2, 0, 0, 0, 0, time.UTC),
			wantErr: false,
		},
		{
			name:    "date with time",
			input:   "2025-01-02T15:04:05Z",
			want:    time.Date(2025, 1, 2, 15, 4, 5, 0, time.UTC),
			wantErr: false,
		},
		{
			name:    "date with time and timezone",
			input:   "2025-01-02T15:04:05+01:00",
			want:    time.Date(2025, 1, 2, 15, 4, 5, 0, time.FixedZone("", 3600)),
			wantErr: false,
		},
		{
			name:    "date with nanoseconds",
			input:   "2025-01-02T15:04:05.123456789Z",
			want:    time.Date(2025, 1, 2, 15, 4, 5, 123456789, time.UTC),
			wantErr: false,
		},
		{
			name:    "old year format",
			input:   "792",
			want:    time.Date(792, 1, 1, 0, 0, 0, 0, time.UTC),
			wantErr: false,
		},
		{
			name:    "invalid format",
			input:   "not-a-date",
			want:    time.Time{},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ParseLucaDateTime(tt.input)
			if tt.wantErr {
				assert.Error(t, err)
				return
			}
			assert.NoError(t, err)
			assert.True(t, got.Equal(tt.want))
		})
	}
}
