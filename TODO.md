# IEX Hist Parser

## Program Components to Write

1. Method to programmatically download past HIST files
2. Read the binary data
3. Decide which messages we want to keep
4. Transform (decode) the data into a Python object format - this is the hard part
5. Design class for storing IEX data
6. Write data to a DB
7. Design DB schema
8. Select a DB to use
9. Unit tests

## Questions

1. How do we keep the DB updated (e.g., with regards to stock splits) - maybe do a periodic refresh
2. How much data do we want to retain?

## External Resources

Download page: https://iextrading.com/trading/market-data/#hist-download
IEX Transport Protocol documentation: https://iextrading.com/docs/IEX%20Transport%20Specification.pdf
IEX TOPS documentation: https://iextrading.com/docs/IEX%20TOPS%20Specification.pdf

