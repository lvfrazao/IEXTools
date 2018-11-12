# IEXTools

v 0.0.3

This package provides tools for working with data provided by IEX's REST API and tools to decode and use IEX's binary market data (dubbed "HIST"). For more information on the type of data offered by IEX please visit their website: <https://iextrading.com/developer/docs> and <https://iextrading.com/trading/market-data/>

## Disclaimers

The author and contributors to this repository are not in any way associated with IEX. This code is provided AS IS with no warranties or any guarantees. It is entirely possible that at any moment this package will not work either due to a programming error or due to a change from IEX.

This package is under active development and may be subject to regular breaking changes.

## Executive Summary

The Investors Exchange (IEX) was founded in 2012 by Brad Katsuyama to combat the effect that high frequency trading was having on other stock exchanges. The story of IEX was made famous by John Lewis in his book, _Fast Boys_.

This package aims to provide a variety of tools for working with stock data provided by IEX such as:

1. The IEX HIST binary data feed files that are freely available through IEX. These files contain nanosecond precision information about stocks such as trades and quotes.
2. The IEX REST API which provides a huge amount of data such as realtime price information for stocks.

## Usage

### Web API

Purpose: Interact with the IEX web API. All methods return Python dictionaries.

The web API has a large number of endpoints returning data:

```Python
>>> from IEXTools import IEX_API
>>> api = IEX_API.IEX_API()
>>> meths = [d for d in dir(api) if not d.startswith('_')]
>>> for i, j, k in zip(meths[::3], meths[1::3], meths[2::3]):
...     print(i.ljust(20), j.ljust(20), k.ljust(20))
...
BASE                 batch                book
chart                collections          company
crypto               deep                 deep_book
deep_trades          delayed_quote        dividends
earnings             earnings_today       effective_spread
financials           hist                 iex_auction
iex_corp_actions     iex_dividends        iex_historical
iex_historical_daily iex_next_day_ex_div  iex_official_price
iex_short_interest   iex_stats_intraday   iex_stats_recent
iex_stats_records    iex_symbols          iex_threshold_securities
largest_trades       last                 logo
market               news                 ohlc
operational_halt     peers                previous
price                quote                relevant
sector_performance   security_event       short_sale_price_test_status
splits               stats                stock_list
symbols              system_event         timeout
timeseries           today_ipos           tops
trade_break          trading_status       upcoming_ipos
```

Users should consult the docstrings of a given function or IEX's docs for additional information on how to use a given endpoint. All endpoints documented in the IEX API docs are implemented in this class.

```Python
>>> help(api.ohlc)
Help on method ohlc in module IEX_API:

ohlc(symbol: str) -> dict method of IEX_API.IEX_API instance
    Returns the open, high, low, and close prices for a given company.

    https://iextrading.com/developer/docs/#ohlc

>>> apple_ohlc = api.ohlc('aapl')
>>> print(IEX_API.pretty_json(apple_ohlc))
{
    "close": {
        "price": 204.47,
        "time": 1541797200568
    },
    "high": 206.01,
    "low": 202.25,
    "open": {
        "price": 205.55,
        "time": 1541773800180
    }
}
```

All symbols available on the API can be retrived using the `symbols` method:

```Python
>>> all_symbols = api.symbols()
>>> len(all_symbols)
8756
>>> api.symbols()[1]
{'symbol': 'AA', 'name': 'Alcoa Corporation', 'date': '2018-11-09', 'isEnabled': True, 'type': 'cs', 'iexId': '12042'}
```

### Downloader

Purpose: Download IEX's pcap files containing nanosecond precision stock data - the so called HIST files.

The `DataDownloader` class can be instantiated without any arguments by simply calling the class.

```Python
d1 = IEXTools.DataDownloader()
```

There are three available methods in this class:

```python
>>> print([method for method in dir(IEXTools.DataDownloader) if not method.startswith('_')])

['decompress', 'download', 'download_decompressed']
```

- download: Downloads the gziped TOPS or DEEP file for a given datetime input
- decompress: Unzips the compressed HIST file into a pcap
- download_decompressed: downloads and decompresses the HIST file - deletes the zipped file at the end

**Warning, IEX HIST files are generally very large (multiple gbs)**

Usage:

```Python
>>> import IEXTools
>>> from datetime import datetime
>>> d1 = IEXTools.DataDownloader()
>>> d1.download_decompressed(datetime(2018, 7, 13), feed_type='tops')
'20180713_IEXTP1_TOPS1.6.pcap'
```

### Parser

Purpose: Parse the binary PCAP / HIST files offered by IEX.

To create a Parser object simply supply the file path as an argument.

```Python
>>> from IEXTools import IEXparser, messages
>>> import IEXparser
>>> import messages
>>> p = IEXparser.Parser(r'IEX TOPS Sample\20180103_IEXTP1_TOPS1.6.pcap')
>>> p
Parser("IEX TOPS Sample\\20180103_IEXTP1_TOPS1.6.pcap", tops=True, deep=False)
```

This instantiates a Parser object with the pcap file opened. You can also optionally specify what type of HIST file you are loading, either TOPS (`tops=True`) or DEEP (`deep=True`).

Use the `get_next_message` method of the Parser object to return a message object. The message objects are documented in the messages.py module. You can optionally specify a list of message classes to restrict the returned messages to only those types.

```Python
>>> allowed = [messages.TradeReport]
>>> p.get_next_message(allowed)
TradeReport(flags=64, timestamp=1514984427833117218, symbol='ZVZZT', size=975, price_int=100150, trade_id=577243)
```

The last message retrieved can also be accessed through the Parser object itself with the `message` attribute. Similarly the message type can be accessed as `Parser.message_type` and the binary encoded message can be accessed with `Parser.message_binary`. The message object also has several attributes that may be accessed (varies by object).

```Python
>>> p.message
TradeReport(flags=64, timestamp=1514984427833117218, symbol='ZVZZT', size=975, price_int=100150, trade_id=577243)
>>> p.message.date_time
datetime.datetime(2018, 1, 3, 13, 0, 27, 833117, tzinfo=datetime.timezone.utc)
>>> p.message.price
10.015
>>> p.message_type
84
>>> p.message_binary
b'@"\xca=uON\x06\x15ZVZZT\xcf\x03\x00\x006\x87\x01\x00\x00\x00\x00\x00\xdb\xce\x08\x00\x00\x00\x00\x00'
```

The program also allows you to use it with a context manager and loop through it like a file:

```Python
with Parser(file_path) as iex_messages:
    for message in iex_messages:
        do_something(message)
```

Benchmarks:
On my personal laptop (Lenovo ThinkPad X1 Carbon, Windows 10):

```text
Beginning test - 1,000,000 messages - all messages, not printing
Parsed 1,000,000 messages in 52.2 seconds -- 19141.6 messages per second

Beginning test - 1,000,000 messages - only TradeReport and QuoteUpdate messages, not printing
Parsed 1,000,000 messages in 54.0 seconds -- 18512.9 messages per second
```

By not specifying the `allowed` argument the parser returns 1,000,000 parsed messages approximately 3% faster. However, in order to return 1,000,000 parsed messages the Parser with the `allowed` argument set may have to read through more than 1,000,000 messages. Testing suggests that actually decoding the message takes about 10 microseconds (130,000 messages per second).

## External References

- HIST Download page: <https://iextrading.com/trading/market-data/#hist-download>
- IEX Transport Protocol documentation: <https://iextrading.com/docs/IEX%20Transport%20Specification.pdf>
- IEX TOPS documentation: <https://iextrading.com/docs/IEX%20TOPS%20Specification.pdf>
- API docs: <https://iextrading.com/developer/docs/>

## Discussion

### Pros

**HIST**

- This is tick by tick historical data offered by IEX for free - other exchanges typically charge large amounts of money for access to similar data

**API**

- The IEX web API provides a vast amount of data and has very high rate limits

### Cons

**HIST**

- Some people say that the quality of data from IEX may be lower due to the lower volume that they handled when compared to other bigger exchanges (not sure how valid this actually is)
- Unsure how this data is maintained (if at all)
- The future availability of this data is not guaranteed, IEX may choose to paywall this data in the future
- Data is unadjusted so it would need to be manually adjusted in order to use in a backtesting engine

**API**

- It appears that the v1 API will be deprecated in the first half of 2019 and will no longer be offered as a free service
- There appears to be many inaccuracies in the data (as seen from a review of their issues page on Github)

### Questions

1. Q: Is the HIST data adjusted for dividends, splits, etc.? If so how often? A: No, HIST data is just a saved version of the live binary trading stream - unadjusted.
2. Q: Am I required to fill out and submit a Data Agreement prior to accessing the data? A: According to the IEX API maintainers this is not required to access the historical data
3. Q: Will this data remain free? A: It appears that there are plans for monetizing the web API in 2019 although there will be a free tier plan offered. The fate of the HIST data has not been divulged.

## Release Notes

### 0.0.1

- `Parser` class - allows decoding of HIST binary data
- `Message` objects defined - each IEX message type defined in TOPS now has an associated Python object

### 0.0.2

- `DataDownloader` class: allows user to download specified HIST files
- Packaging for easy PIP install
- Added context manager and iteration support to `Parser` object
- Added typing support
- Added some test coverage (still needs improvement)

### 0.0.3

- Bug fix: Circular import issue with AllMessages from the TypeAliases file
- Security: Upgraded requests library to 2.20.0 due to vulnerability
- `IEX_API` class: allows the user to access all endpoints of the IEX REST API v1

### Future Focus

- Need additional tests
- Review typing functionality

## Requirements

- Python 3.7
- requests
