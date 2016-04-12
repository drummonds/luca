# Management account process
###### Updated 2016-04-04

Want to change the process so that the management accounts are essentially a push button operation.

There are two ways of calculating the accounts and I want to do both of them to make up the following requirements:

1. Print Historic records
2. Print Current accounts
3. Make current record the official version (convert a draft accounts to final)
4. To check or eliminate by automating the current checks for the end of a month, eg petty cash reconciliation, COGS adjustments etc

### Printing historic records
This is interesting as it ensures that you can:

- Format and print an excel spreadsheet
- Have a record of historic management accounts

## Development priorities

- Create Excel BS format
- Check all data for integrity
- *Get trial balance data from Sage* Extraction of trial balance data from Sage directly
	- Verify that the data is the same as the transaction trial balance produced by sage.

- *Convert chart of accounts*


### TODO
These are ideas which came up which I decided not to implement but could be implemented.   

- ? Add details on each import
- change reporting to correct sign covert from list of dataframes to a single dataframe and a list of columns   
- A more detailed chart of accounts so that P&L is created more automatically - eg Profit, Cost of Sales, variable works expense, fixed works expense, admin expenses etc.   

