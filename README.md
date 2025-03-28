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

This is used as the date the book keeper is aware of the information. you might also refer date as
"value date" and Knowledge date as "insertion date". For accountants preparing books of accounts it
allows them to say that as of date X we were told the accounts were Y but with new information on date P
the accounts are now Q.

## Journal Documents and Ledger

I am going to use ledger for the complete set of accounts. There are other meanings but this seems to be closest
to historical meaning.

Journals can also be calculated on different basis eg models which can be much more compact, eg recurring entries.

The documents are defined as the collection of text files and we can parse into them and out. The books
is an internal representation of the accunts which is built from the journals.

# EBNF definition of text format

Using the language of Martin Blais Beancount https://beancount.github.io/docs/beancount_language_syntax.html#syntax-overview

Currently it is a lot simplified:

- no option entries
- no balance postings

Luca document its own usage.  Note it has a more relaxed input format and a more
precise output format.  So for instance files can be input any order but will be saved in sorted order.  
Open directives allow a default commodity but when saved it will be specified.
The following is the output of the luca ebnf output:

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

The resolution of datetime is assumed to be 1 microsecond. Note that different versions might
implement it with different resolutions to squeeze the amount of storage. Eg the default
datetime uses Unix Epoch timestamps

## Implementation details

Pacioli has 4 types of records which are used to hold the accounting data:

- Inventory of goods and money
- Day notebooks, voluminous contemporaneous diaries
- Journal entries. In chonological order with notes (cross referenced to the ledger)
- Ledgers Summary of activity by account

With a computer we are going to focus on the journal. The cross referencing and ledger balances can
be produced by computation.

- Commodity
- Account
- Transaction
- Balance

The core concept is to take Pacioli's books and conentate on the journal entries. In order for this
to be complete you need to be able to extne

There are a number of domains:

- parsing
  - Serialisation to and from text
- Core manipulation
- Balance query functions

#### Serialisation

- internal/datetime: Support LucaDateTimeString
- directiveHeader: Generic directive header

#### Core

- directive: interface
- journal: list of entries
- directives
  - commodity
  - account
  - transaction
  - balance


### Road map

```mermaid
gantt
    title Luca Roadmap
    dateFormat  YYYY-MM-DD

    section Timelines
    Phase 0 Live         :t1,  2025-02-06, 6M
    Phase 1 Enhance reporting     :t2,  after t1, 6M

    section Phase 0 Live
    Text serialisation    : done, a1, 2025-02-06, 6w
    Single file ingestion and saving : a11, after a1, 1w
    Multiple file ingestion and saving : a12, after a11, 1w
    Balance reporting : a13, after a12, 1w
    AFP sample : a14, after a13, 1w
    Ofx Ingestion         :active, a2, after a14, 1M
    Plain reporting       :a3, after a2, 1M
    Web reporting         :a4, after a3, 1M
    Useful                :milestone, a5, after a4, 1d
    Sql query language    :a6, after a5, 1M

```



## Features

The software architecture of Luca looks like this:

``` mermaid
graph TB
    subgraph CLI["cmd/luca"]
        CLI_MAIN["main.go"]
        AFP["afp.go"]
        TEMPLATES["templates/"]
    end

    subgraph Core["github.com/drummonds/luca"]
        LEDGER["Ledger"]
        SUMMARY["summary.go"]
        ACCOUNT["Account"]
        TRANSACTION["Transaction"]
        MOVEMENT["Movement"]
    end

    subgraph Internal["internal/"]
        PARSER["parser/"]
        MERMAID["mermaid/"]
        DATETIME["datetime/"]
    end

    %% Relationships
    CLI_MAIN --> AFP
    AFP --> TEMPLATES
    AFP --> LEDGER
    AFP --> PARSER
    
    LEDGER --> SUMMARY
    SUMMARY --> MERMAID
    LEDGER --> ACCOUNT
    LEDGER --> TRANSACTION
    TRANSACTION --> MOVEMENT
    
    PARSER --> LEDGER
    PARSER --> DATETIME

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef core fill:#BCE,stroke:#333,stroke-width:2px;
    classDef cli fill:#CDA,stroke:#333,stroke-width:2px;
    classDef internal fill:#EEB,stroke:#333,stroke-width:2px;
    
    class CLI_MAIN,AFP,TEMPLATES cli;
    class LEDGER,SUMMARY,ACCOUNT,TRANSACTION,MOVEMENT core;
    class PARSER,MERMAID,DATETIME internal;
```


List of features that will get implmented

### Directive Account

#### Commodity

- Make sure default commodity is defined either explicitly or implicitly
- Save file format use explicit commodity although input format

Allow list rather than single commodity/currency.  This will generate multiple account for each commodity.  
Worked example with Swedish Ore and Canadian dollar.

#### Sub unit clean up 
Spring decimal uses nice rounding system and we should use this rather than subunit.

# Ideas

## Segmenting time
Segmenting by time period. This allows you to deal with all the data for a period in memory
as well as handling longer time periods.

## indexing account movements

It might be worth testing keeping all movements just as a slice and iterating
through them for balances of different types.

There may be an interactiong with periods and having old immutable periods.

# Appendix

## References

date time format comes from https://www.rfc-editor.org/rfc/rfc3339

## String concatenation

You could use either + or stringbuilder. This article https://dev.to/jonathanlawhh/golang-string-concatenation-what-how-why-3fcd
shows that for adding 2 strings both methods are fast but

- is twice as fast. However by the time you get to 10 strings stringbuilder is twice as fast.

So using `"\t" + test.data + "/n"` is clear and good practice but not much longer.

## colophon

This is third version of luca. The first was a python sqlite implementation, the second a
more generic Python version and this a go implmention of a plain text accounting format,

I have read Luca Paciolo's book in translation and think it is admirably clear. I used to
worry that he was taking credit from Benedeto Cotrugli who wrote earlier and was ppublished
later. However Paciolo's book is so clear that I am happy to call this luca.
