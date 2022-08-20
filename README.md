# luca
Python accounting tools for transactions and trial balance manipulation.

The first version of this was quite different using a SQLite database.

I am relooking at an abtract representation of accounts and transactions based on plain text accounting.

Using beancount as a reference there are a number of changes:

1) Support from microsecond based ordering of events
2) Aiming to support small numbers of transactions eg up to 10,000
3) Storage an conversion to a text/json
   a) the text format will not have an ordering
4) Support for bitemporal functions which will be used to support a knowledge date
5) Suport fo digital twins for comparing two similar list of transactions perhaps with one generated dynamically


The exploration will be done in ipython notebooks in directory notes
