# IEX_tools

v 0.0.2

This package provides tools to decode and use IEX's binary market data (dubbed "HIST"). For more information on the type of data offered by IEX please visit their website: <https://iextrading.com/trading/market-data/>

## Disclaimer

The author and contributors to this repository are not in any way associated with IEX. This code is provided AS IS with no warranties or any guarantees. It is entirely possible that at any moment this package will not work either due to a programming error or due to a change from IEX.

## Executive Summary

The Investors Exchange (IEX) was founded in 2012 by Brad Katsuyama to combat the effect that high frequency trading was having on other stock exchanges. The story of IEX was made famous by John Lewis in his book, _Fast Boys_.

This package aims to provide a variety of tools for using the IEX HIST binary data feed files that are freely available through IEX. These files contain nanosecond precision information about stocks such as trades and quotes.

## Usage

### Downloader

The `DataDownloader` class can be instantiated without any arguments by simply calling the class.

```Python
d1 = IEX_hist_parser.DataDownloader()
```

There are three available methods in this class:

```python
>>> print([method for method in dir(IEX_hist_parser.DataDownloader) if not method.startswith('_')])

['decompress', 'download', 'download_decompressed']
```

- download: Downloads the gziped TOPS or DEEP file for a given datetime input
- decompress: Unzips the compressed HIST file into a pcap
- download_decompressed: downloads and decompresses the HIST file - deletes the zipped file at the end

**Warning, IEX HIST files are generally around 500mb compressed >1.5gb uncompressed**

Usage:

```Python
>>> import IEX_hist_parser
>>> from datetime import datetime
>>> d1 = IEX_hist_parser.DataDownloader()
>>> d1.download_decompressed(datetime(2018, 7, 13), feed_type='tops')
'20180713_IEXTP1_TOPS1.6.pcap'
```

### Parser

To create a Parser object simply supply the file path as an argument.

```Python
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

- Download page: <https://iextrading.com/trading/market-data/#hist-download>
- IEX Transport Protocol documentation: <https://iextrading.com/docs/IEX%20Transport%20Specification.pdf>
- IEX TOPS documentation: <https://iextrading.com/docs/IEX%20TOPS%20Specification.pdf>

## Discussion

### Pros

- This is tick by tick historical data offered by IEX for free - other exchanges typically charge large amounts of money for access to similar data

### Cons

- Some people say that the quality of data from IEX may be lower due to the lower volume that they handled when compared to other bigger exchanges (not sure how valid this actually is)
- Unsure how this data is maintained (if at all)
- The future availability of this data is not guaranteed, IEX may choose to paywall this data in the future
- Data is unadjusted so it would need to be manually adjusted in order to use in a backtesting engine

### Questions

1. Q: Is the HIST data adjusted for dividends, splits, etc.? If so how often? A: No, HIST data is just a saved version of the live binary trading stream - unadjusted.
2. Q: Am I required to fill out and submit a Data Agreement prior to accessing the data? A: According to the IEX API maintainers this is not required to access the historical data