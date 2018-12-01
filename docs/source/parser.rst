Parser
======

Usage
-----

Purpose: Parse the binary PCAP / HIST files offered by IEX.

To create a Parser object simply supply the file path as an argument.

   >>> from IEXTools import Parser, messages
   >>> p = Parser(r'IEX TOPS Sample\20180103_IEXTP1_TOPS1.6.pcap')
   >>> p
   Parser("IEX TOPS Sample\\20180103_IEXTP1_TOPS1.6.pcap", tops=True, deep=False)

This instantiates a Parser object with the pcap file opened. You can also optionally specify what type of HIST file you are loading, either TOPS (`tops=True`) or DEEP (`deep=True`).

Use the `get_next_message` method of the Parser object to return a message object. The message objects are documented in the messages.py module. You can optionally specify a list of message classes to restrict the returned messages to only those types.

   >>> allowed = [messages.TradeReport]
   >>> p.get_next_message(allowed)
   TradeReport(flags=64, timestamp=1514984427833117218, symbol='ZVZZT', size=975, price_int=100150, trade_id=577243)

The last message retrieved can also be accessed through the Parser object itself with the `message` attribute. Similarly the message type can be accessed as `Parser.message_type` and the binary encoded message can be accessed with `Parser.message_binary`. The message object also has several attributes that may be accessed (varies by object).

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

The program also allows you to use it with a context manager and loop through it like a file::

   with Parser(file_path) as iex_messages:
       for message in iex_messages:
           do_something(message)

Benchmarks
On my personal laptop (Lenovo ThinkPad X1 Carbon, Windows 10)::

   Beginning test - 1,000,000 messages - all messages, not printing
   Parsed 1,000,000 messages in 52.2 seconds -- 19141.6 messages per second
   
   Beginning test - 1,000,000 messages - only TradeReport and QuoteUpdate messages, not printing
   Parsed 1,000,000 messages in 54.0 seconds -- 18512.9 messages per second

By not specifying the `allowed` argument the parser returns 1,000,000 parsed messages approximately 3% faster. However, in order to return 1,000,000 parsed messages the Parser with the `allowed` argument set may have to read through more than 1,000,000 messages. Testing suggests that actually decoding the message takes about 10 microseconds (130,000 messages per second).

Module Docs
-----------

.. automodule:: IEXTools.IEXparser
   :members:

.. autoclass:: Parser
    :members:

Indices and tables
------------------
 
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
