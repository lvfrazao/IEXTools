#! /usr/bin/python
"""
Collection of tests that I have been using to perform various benchmarks on
parts of the parser.
"""
from IEXparser import Parser
import messages
from datetime import datetime, timezone
from timeit import default_timer


def benchmark(file_path, num_msgs, allowed, symbols=None, printing=False):
    p = Parser(file_path)
    try:
        for i in range(num_msgs):
            p.get_next_message(allowed=allowed)
            if hasattr(p, "symbol"):
                if (p.message.symbol in symbols or not symbols) and printing:
                    print(p.message, p.message.date_time)
            else:
                if printing:
                    print(p.message, p.message.date_time)

    except Exception as e:
        print(p.message_type)
        raise

    return p.bytes_read


def benchmark_allowed(file_path, num_msgs):
    """
    Understand performance implications of passing a list of "allowed" message
    types.

    Results:
    Beginning test - 1,000,000 messages - all messages, not printing
    Parsed 1,000,000 messages in 52.2 seconds -- 19141.6 messages per second
    Beginning test - 1,000,000 messages - only TradeReport and QuoteUpdate messages, not printing
    Parsed 1,000,000 messages in 54.0 seconds -- 18512.9 messages per second
    """
    allowed = None
    symbols = None
    printing = False
    print(
        f"Beginning test - {num_msgs:,d} messages - all messages, not printing"
    )
    start = default_timer()
    bytes_read = benchmark(file_path, num_msgs, allowed, symbols, printing)
    total = default_timer() - start
    print(
        f"Parsed {num_msgs:,d} messages in {total:.1f} seconds -- "
        f"{num_msgs/total:.1f} messages per second\n"
        f"{bytes_read/(1024**2)/total:.2f} mb/s"
    )

    allowed = [messages.TradeReport, messages.QuoteUpdate]
    symbols = None
    printing = False
    print(
        f"Beginning test - {num_msgs:,d} messages - only TradeReport and "
        f"QuoteUpdate messages, not printing"
    )
    start = default_timer()
    bytes_read = benchmark(file_path, num_msgs, allowed, symbols, printing)
    total = default_timer() - start
    print(
        f"Parsed {num_msgs:,d} messages in {total:.1f} seconds -- "
        f"{num_msgs/total:.1f} messages per second\n"
        f"{bytes_read/(1024**2)/total:.2f} mb/s"
    )


def test_allowed(file_path, num_msgs):
    allowed = [messages.TradeReport, messages.QuoteUpdate]
    allowed = [messages.TradeReport]
    symbols = None
    printing = True
    print(
        f"Beginning test - {num_msgs:,d} messages - only TradeReport and "
        f"QuoteUpdate messages, not printing"
    )
    start = default_timer()
    benchmark(file_path, num_msgs, allowed, symbols, printing)
    total = default_timer() - start
    print(
        f"Parsed {num_msgs:,d} messages in {total:.1f} seconds -- "
        f"{num_msgs/total:.1f} messages per second"
    )


def decode_benchmark(num_times):
    """
    Objective understand the speed at which decoding of binary data occurs with
    the struct.unpack function. This is the current hypothetical top speed for
    the program on one process.
    Results:
    Decoded 1,000,000 messages in 8.8 seconds -- 113169.2 messages per second
    Time to decode one message is 8.836324765 microseconds
    """
    start = default_timer()
    for i in range(num_times):
        b1 = (
            b"\x00\x00\x00\x40\x22\xca\x3d\x75\x4f\x4e\x06\x15\x5a\x56\x5a\x5a"
            b"\x54\xcf\x03\x00\x06\x87\x01\x00\x00\x00\x00\x00\xdb\xce\x08\x00"
            b"\x00\x00\x00\x00"
        )
        messages.decode_message(84, b1)
    total = default_timer() - start
    print(
        f"Decoded {num_times:,d} messages in {total:.1f} seconds -- "
        f"{num_times/total:.1f} messages per second"
    )
    print(
        f"Time to decode one message is {total/num_times * 10**6} microseconds"
    )


def test_price(file_path):
    """
    Show that price calculation being done in Messages parent class is being
    properly inherited.
    """
    p = Parser(file_path)
    allowed = [messages.AuctionInformation]
    p2 = p.get_next_message(allowed)

    for attrib in p2.__slots__:
        print(f"{attrib} = {getattr(p2, attrib)}")


if __name__ == "__main__":
    file_path = r"C:\Users\luiz_\Dropbox\Personal\Python\Programs\IEX_hist_parser\IEX TOPS Sample\20180103_IEXTP1_TOPS1.6.pcap"
    benchmark_allowed(file_path, 10 ** 6)
    # test_allowed(file_path, 10**5)
    # decode_benchmark(10**6)
    # test_price()
