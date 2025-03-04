# luca

This is a plain text go library to manipulate and record accounting journal entries. It
inherits ideas from [Luca Pacioli translated by Geijsbeek][pacioli], [Martin Blais' Beancount][beancount] and a lot from [Kobetic's coin][coin].

[beancount](https://beancount.github.io/docs/beancount_language_syntax.html#accounts)
[coin](https://github.com/drummonds/luca/internal)
[pacioli](https://archive.org/details/ancientdoubleent00geijuoft)

## Digital representations

There will be three representations of the data which will be supported:
- A plain text account format (storage only)
- An in memory version for fast transformation
- A database format for larger scale

### Plain text form .luca

This is a storage format and will be transformed to the in memory or database
form for conversion.

Using Beancount as a reference there are a number of changes:

1. Support for nanosecond based ordering of events
2. Support for bitemporal functions which will be used to support a knowledge date
3. Suport for digital twins for comparing two similar journal books.

### In memory form

Operations will be defined on this:

- Read from text and Db forms
- creating balances at time X knowledge date y
- reporting data eg P&L for a period


## Differences from Coin

- Different dateformats
- Addition of Knowledge date
- Uses commodity movements as core item rather than posting entries
- Uses alecthomas/participle/ as parser rather than own version
- Seperates Text representation models from core accounts model, Ledger or a Pacioloi had Quaderno

## Knowledge date

This is used as the date the book keeper is aware of the information.  you might also refer date as
"value date" and Knowledge date as "insertion date".  For accountants preparing books of accounts it 
allows them to say that as of date X we were told the accounts were Y but with new information on date P
the accounts are now Q.

## Documents and Ledger

crypto usage which is more closely related to journal entries.  So quaderno it is.
I am going to use ledger for the complete set of accounts.  There are other meanings but this seems to be closest
to historical meaning.

Quaderno can also be calculated on different basis eg models which can be much more compact.

The documents are defined as the collection of text files and we can parse into them and out.  The books
is an internal representation of the accunts which is built from the journals. 


# EBNF definition of text format

Using the language of Martin Blais Beancount https://beancount.github.io/docs/beancount_language_syntax.html#syntax-overview

Current it is a lot simplified:

- no option entries
- no balance postings

Luca document its own usage, and the following is the output:

```ebnf

Grammar:
Document = Entry* .
Entry = <comment>* <date> <knowledgedate>? (Transaction | Account | Commodity | GenericEntry) .
Transaction = ("txn" | "*") <string>? ("INDENT" Movement+ "DEDENT")? .
Movement = <ident> <number> <arrow> <ident> .
Account = "open" <ident> <ident>? ("INDENT" AccountDetail "DEDENT")? .
AccountDetail = ("description" <string>)? .
Commodity = "commodity" <ident> ("INDENT" CommodityDetail "DEDENT")? .
CommodityDetail = ("description" <string>)? ("subunit" <number>)? .
GenericEntry = "generic" <string>? <comment>? ("INDENT" SubDirective+ "DEDENT")? .
SubDirective = <string> .
```

Notes:
For directives apart from transactions full_date is assumed at the start of the day, and for transactions one microsecond before the end of the day.
Directives names are lower case.

The resolution of datetime is assumed to be 1 microsecond.  Note that different versions might
implement it with different resolutions to squeeze the amount of storage. Eg the default
datetime uses Unix Epoch timestamps

## Implmentation details

Pacioli has 4 types of records which are used to hold the accounting data:

- Inventory of goods and money
- Day notebooks, voluminous contemporaneous diaries
- Journal entries.  In chonological order with notes (cross referenced to the ledger)
- Ledgers Summary of activity by account

With a computerf we are going to focus on the journal.  The cross referencing and ledger balances can
be produced by computation.

- Commodity
- Account
- Transaction
- Balance

The core concept is to take Pacioli's books and conentate on the journal entries.  In order for this
to be complete you need to be able to extne

There are a number of domains:

- parsing
    - Serialisation to and from text
- Core manipulation
- Balance query functions


### Hierarchy of implementation

At the base level you have some helper functions:

#### Serialisation

- internal/datetime:  Support LucaDateTimeString
- directiveHeader: Generic directive header

#### Core

- directive: interface
- journal: list of entries
- directives
    - commodity
    - account
    - transaction
    - balance

# Ideas
Segmenting by time period.  This allows you to deal with all the data for a period in memory 
as well as handling longer time periods.

## References

date time format comes from https://www.rfc-editor.org/rfc/rfc3339

### String concatenation

You could use either + or stringbuilder.  This article https://dev.to/jonathanlawhh/golang-string-concatenation-what-how-why-3fcd 
shows that for adding 2 strings both methods are fast but 
+ is twice as fast.  However by the time you get to 10 strings stringbuilder is twice as fast.

So using `"\t" + test.data + "/n"` is clear and good practice but not much longer. 

## colophon

This is third version of luca.  The first was a python sqlite implementation, the second a
more generic Python version and this a go implmention of a plain text accounting format,

I have read Luca Paciolo's book in translation and think it is admirably clear. I used to 
worry that he was taking credit from Benedeto Cotrugli who wrote earlier and was ppublished
later.  However Paciolo's book is so clear that I am happy to call this luca.