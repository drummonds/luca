# luca

Python accounting tools for transactions and trial balance manipulation.

The first version of this was quite different using a SQLite database.

I am relooking at an abtract representation of accounts and transactions based on plain text accounting.

Using beancount as a reference there are a number of changes:

1. Support from microsecond based ordering of events
2. Aiming to support small numbers of transactions eg up to 10,000
3. Storage an conversion to a text/json
   a) the text format will not have an ordering
4. Support for bitemporal functions which will be used to support a knowledge date
5. Suport fo digital twins for comparing two similar list of transactions perhaps with one generated dynamically

The exploration will be done in ipython notebooks in directory notes

# Introduction

My aim here is use plain text accounting to create a simple python model for modelling accounting. This will be used to answer such questions as what is the balance of an account at time x

A great collection of reference material on plain text accounting is here https://plaintextaccounting.org/ and I particulary want to highlight Martin Kleppmann https://martin.kleppmann.com/2011/03/07/accounting-for-computer-scientists.html

## Starting

```ledger
2022-07-23T23:59:58 * "Accrue interest"
  Expense:PnL    -0.12345
  Liabilities:Client
```

# EBNF definition of text format

Using the language of Martin Blais Beancount https://beancount.github.io/docs/beancount_language_syntax.html#syntax-overview

Current it is a lot simplified:

- no option entries
- no commodities
- no currencies
- no balance postings

I have tried to document it use W3C EBNF description https://www.w3.org/TR/xml/#sec-notation

```ebnf

journal ::= entry*
entry ::= comment | transaction
comment ::= WS* ";" AllChar* EOL
transaction ::= header postings
postings ::= posting posting posting*

directive ::= value-date {^knowledge-date} {* transaction | 'open' open-directive | 'balance' balance-directive}
blank-line ::= \n;
header ::= value white_space id  \n;
value-date ::= (full-date | date-time);
knowledge-date ::= (full-date | date-time);
white-space ::= ? white space characters ? ;
posting = account { {asset-class};
balance-posting = account;
id = string;
comment = string;
string ::= '"' AllChar* '"'


account = (`Assets` | `Liabilities` | `Equity` | `Income` | 'Expenses') : name
name = TEXT | TEXT : name

date-fullyear   = 4DIGIT
date-month      = 2DIGIT  ; 01-12
date-mday       = 2DIGIT  ; 01-28, 01-29, 01-30, 01-31 based on
                          ; month/year
time-hour       = 2DIGIT  ; 00-23
time-minute     = 2DIGIT  ; 00-59
time-second     = 2DIGIT  ; 00-58, 00-59, 00-60 based on leap second
                          ; rules
time-secfrac    = "." 1*DIGIT
time-numoffset  = ("+" / "-") time-hour ":" time-minute
time-offset     = "Z" / time-numoffset

partial-time    = time-hour ":" time-minute ":" time-second
                  [time-secfrac]
full-date       = date-fullyear "-" date-month "-" date-mday
full-time       = partial-time time-offset

date-time       = full-date "T" full-time

NameStartChar	   ::=   	":" | [A-Z] | "_" | [a-z] | [#xC0-#xD6] | [#xD8-#xF6] | [#xF8-#x2FF] | [#x370-#x37D] | [#x37F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF]
[4a]   	NameChar	   ::=   	NameStartChar | "-" | "." | [0-9] | #xB7 | [#x0300-#x036F] | [#x203F-#x2040]

AllChar ::== Char | WS
Char ::=  ":" | NameStartChar | NameChar
NameStartChar ::= ([A-Z] | "_" | [a-z] | [#xC0-#xD6] | [#xD8-#xF6] | [#xF8-#x2FF] | [#x370-#x37D] |
                  [#x37F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] |
                  [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF])
NameChar ::=  NameStartChar | "-" | "." | [0-9] | #xB7 | [#x0300-#x036F] | [#x203F-#x2040]
WS ::= #x20 | #x9 | UnicodeWS
UnicodeWS ::= (x00A0 | x1680 | x2000 | x2001 | x2002 | x2003 | x2004 | x2005 |
               x2006 | x2007 | x2008 | x2009 | x200A | x2028 | x2029 | x202F |
               x205F | x3000)
EOL ::=  #xD #xA| #xA
```

Notes:
For directives apart from transactions full_date is assumed at the start of the day, and for transactions one microsecond before the end of the day.

The resolution of datetime is assumed to be 1 microsecond

## Signs

The accounting equation is:

$$ Assets = Liabilities + Equity + Income − Expenses$$

Where:

$$Equity = ContributedCapital - Dividends$$

In a computer system we usually use +ve and -ve to as opposed to Credit and Debit which are the traditional accounting forms of increasing and decreasing then the equation is:

$$ Assets - Liabilities - Equity - Income + Expenses = 0$$

So this give you:

| Account Types | Increase |
| ------------- | -------- |
| Assets        | +        |
| Liabilities   | -        |
| Equity        | -        |
| Income        | -        |
| Expenses      | +        |

## References

date time format comes from https://www.rfc-editor.org/rfc/rfc3339
