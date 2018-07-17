# IEX Hist Parser

## Overall Objective

Build a small DB with the IEX historical data to perform backtesting of trading strategies.

## Program Components to Write

1. Method to programmatically download past HIST files
2. ~~Read the binary data~~
3. Decide which messages we want to keep
4. ~~Transform (decode) the data into a Python object format~~
5. ~~Design class for storing IEX data~~
6. Design DB schema
7. Select a DB to use
8. Write data to a DB
9. Unit tests
10. Analyze the universe of stocks available through IEX
11. Analyze how many messages per second are sent vs. how fast I can process through them -- Will I be able to do this in real time?
12. How can I backtest strategies using this dataset?
13. What other functionality do I need to add?
14. Proper packaging and hosting on PyPi
15. Pick a new cooler name for this project

## External Resources

Download page: <https://iextrading.com/trading/market-data/#hist-download>
IEX Transport Protocol documentation: <https://iextrading.com/docs/IEX%20Transport%20Specification.pdf>
IEX TOPS documentation: <https://iextrading.com/docs/IEX%20TOPS%20Specification.pdf>
