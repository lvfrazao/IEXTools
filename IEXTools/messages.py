"""
messages.py
Holds the classes for the different message types and helps the Parser class
decode messages. All information for parsing messages is derived from the
specifications published by IEX on their website as "IEX TOPS Specification":
https://iextrading.com/docs/IEX%20TOPS%20Specification.pdf
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import struct
from typing import Dict, Union, Type
from .IEXHISTExceptions import ProtocolException


# Debating whether this should just be a class variable of SystemEvent. I'm
# afraid that placing it in the class will create a copy of this dict for every
# instance of SystemEvent.
system_event_types = {
    79: "start_of_messages",
    83: "start_of_system_hours",
    82: "start_of_regular_hours",
    67: "end_of_messages",
    69: "end_of_system_hours",
    77: "end_of_regular_hours",
}

trading_status_messages = {
    "H": "Trading halted across all US equity markets",
    "O": "Trading halt released into an Order Acceptance Period on IEX "
    "(IEX-listed securities only)",
    "P": "Trading paused and Order Acceptance Period on IEX "
    "(IEX-listed securities only)",
    "T": "Trading on IEX",
}


class MessageDecoder(object):
    def __init__(self, version: float = 1.6) -> None:
        """
        Some notes on data types used in decoding IEX messages:
        B: unsigned byte
        H: short unsigned int (2 bytes)
        L: long unsigned int (4 bytes)
        s: string (size denoted by preceding number)
        q: signed long long (8 bytes)
        """
        self.message_types: Dict[
            float, Dict[bytes, Dict[str, Union[str, AllMessages]]]
        ] = {
            1.0:{
                b"\x53": {
                    "str": "System Event Message",
                    "cls": SystemEvent,
                    "fmt": "<Bq",
                },
                b"\x44": {
                    "str": "Security Directory Message",
                    "cls": SecurityDirective,
                    "fmt": "<Bq8sLqB",
                },
                b"\x48": {
                    "str": "Trading Status Message",
                    "cls": TradingStatus,
                    "fmt": "<1sq8s4s",
                },
                b"\x4f": {
                    "str": "Operational Halt Status Message",
                    "cls": OperationalHalt,
                    "fmt": "<1sq8s",
                },
                b"\x50": {
                    "str": "Short Sale Price Test Status Message",
                    "cls": ShortSalePriceSale,
                    "fmt": "<Bq8s1s",
                },
                b'\x45': {
                    "str": "Security Event Message",
                    "cls": SecurityEvent,
                    "fmt": "<Bq8s"
                },
                b'\x38':{
                    "str": "Bid Price Level Update Message",
                    "cls": BidPriceLevelUpdate,
                    "fmt": "<Bq8slq"
                },
                b'\x35':{
                    "str": "Ask Price Level Updte Message",
                    "cls": AskPriceLevelUpdate,
                    "fmt": "<Bq8slq"
                },
                b"\x54": {
                    "str": "Trade Report Message",
                    "cls": TradeReport,
                    "fmt": "<Bq8sLqq",
                },
                b"\x58": {
                    "str": "Official Price Message",
                    "cls": OfficialPrice,
                    "fmt": "<1sq8sq",
                },
                b"\x42": {
                    "str": "Trade Break Message",
                    "cls": TradeBreak,
                    "fmt": "<1sq8sLqq",
                },
                b"\x41": {
                    "str": "Auction Information Message",
                    "cls": AuctionInformation,
                    "fmt": "<1sq8sLqqL1sBLqqqq",
                },
            },
            1.6: {
                b"\x53": {
                    "str": "System Event Message",
                    "cls": SystemEvent,
                    "fmt": "<Bq",
                },
                b"\x44": {
                    "str": "Security Directory Message",
                    "cls": SecurityDirective,
                    "fmt": "<Bq8sLqB",
                },
                b"\x48": {
                    "str": "Trading Status Message",
                    "cls": TradingStatus,
                    "fmt": "<1sq8s4s",
                },
                b"\x4f": {
                    "str": "Operational Halt Status Message",
                    "cls": OperationalHalt,
                    "fmt": "<1sq8s",
                },
                b"\x50": {
                    "str": "Short Sale Price Test Status Message",
                    "cls": ShortSalePriceSale,
                    "fmt": "<Bq8s1s",
                },
                b"\x51": {
                    "str": "Quote Update Message",
                    "cls": QuoteUpdate,
                    "fmt": "<Bq8sLqqL",
                },
                b"\x54": {
                    "str": "Trade Report Message",
                    "cls": TradeReport,
                    "fmt": "<Bq8sLqq",
                },
                b"\x58": {
                    "str": "Official Price Message",
                    "cls": OfficialPrice,
                    "fmt": "<1sq8sq",
                },
                b"\x42": {
                    "str": "Trade Break Message",
                    "cls": TradeBreak,
                    "fmt": "<1sq8sLqq",
                },
                b"\x41": {
                    "str": "Auction Information Message",
                    "cls": AuctionInformation,
                    "fmt": "<1sq8sLqqL1sBLqqqq",
                },
            },
            1.5: {
                b"\x51": {
                    "str": "Quote Update Message",
                    "cls": QuoteUpdate,
                    "fmt": "<Bq8sLqqL",
                },
                b"\x54": {
                    "str": "Trade Report Message",
                    "cls": TradeReport,
                    "fmt": "<Bq8sLqqxxxx",
                },
                b"\x42": {
                    "str": "Trade Break Message",
                    "cls": TradeBreak,
                    "fmt": "<1sq8sqqxxxx",
                },
            },
        }
        self.DECODE_FMT: Dict[int, str] = {
            msg[0]: self.message_types[version][msg]["fmt"]
            for msg in self.message_types[version]
        }
        self.MSG_CLS: Dict[int, Type[AllMessages]] = {
            msg[0]: self.message_types[version][msg]["cls"]
            for msg in self.message_types[version]
        }

    def decode_message(self, msg_type: int, binary_msg: bytes) -> AllMessages:
        try:
            fmt = self.DECODE_FMT[msg_type]
        except KeyError as e:
            raise ProtocolException(f"Unknown message type: {e.args}")
        decoded_msg = struct.unpack(fmt, binary_msg)
        msg = self.MSG_CLS[msg_type](*decoded_msg)
        return msg


@dataclass
class Message(object):
    """
    Superclass to all message types - should never be instantiated.

    Grouping common operations among the different message types. Processes any
    bytes objects into string objects and computes the prices in messages as
    floats.
    """

    __slots__ = "date_time"

    def __post_init__(self):
        self.date_time = datetime.fromtimestamp(
            self.timestamp / 10 ** 9, tz=timezone.utc
        )
        str_fields = "symbol", "status", "reason", "detail", "halt_status"
        for attrib in str_fields:
            if hasattr(self, attrib):
                if isinstance(getattr(self, attrib), bytes):
                    setattr(self, attrib, getattr(self, attrib).decode("utf-8").strip())

        int_prices = [p for p in self.__slots__ if "price" in p and "int" in p]

        for int_price in int_prices:
            attrib = int_price.split("_int")[0]
            setattr(self, attrib, getattr(self, int_price) / 10 ** 4)


@dataclass
class SystemEvent(Message):
    """
    From the TOPS specification document: "The System Event Message is used to
    indicate events that apply to the market or the data feed. There will be a
    single message disseminated per channel for each System Event type within a
    given trading session."
    """

    __slots__ = ("system_event", "timestamp", "system_event_str")
    system_event: int  # 1 byte
    timestamp: int  # 8 bytes

    def __post_init__(self):
        Message.__post_init__(self)
        self.system_event_str = system_event_types[self.system_event]


@dataclass
class SecurityDirective(Message):
    """
    From the TOPS specification document: "IEX disseminates a full pre-market
    spin of Security Directory Messages for all IEX-listed securities. After
    the pre-market spin, IEX will use the Security Directory Message to relay
    changes for an individual security"
    """

    __slots__ = (
        "flags",
        "timestamp",
        "symbol",
        "round_lot_size",
        "adjusted_poc_close",
        "luld_tire",
        "price",
    )
    flags: int  # 1 byte
    timestamp: int  # 8 bytes
    symbol: str  # 8 bytes
    round_lot_size: int  # 4 bytes
    adjusted_poc_close: int  # 8 bytes
    luld_tire: int  # 1 byte


@dataclass
class TradingStatus(Message):
    """
    From the TOPS specification document: "The Trading Status Message is used
    to indicate the current trading status of a security."

    The reason string is also defined in the docs:
    - Trading Halt Reasons
        o T1: Halt News Pending
        o IPO1: IPO Not Yet Trading
        o IPOD: IPO Deferred
        o MCB3: Market-Wide Circuit Breaker Level 3 Breached
        o NA: Reason Not Available
    - Order Acceptance Period Reasons
        o T2: Halt News Dissemination
        o IPO2: IPO Order Acceptance Period
        o IPO3: IPO Pre-Launch Period
        o MCB1: Market-Wide Circuit Breaker Level 1 Breached
        o MCB2: Market-Wide Circuit Breaker Level 2 Breached
    """

    __slots__ = ("status", "timestamp", "symbol", "reason", "trading_status_message")
    status: str  # 1 byte
    timestamp: int  # 8 bytes, nanosecond epoch time
    symbol: str  # 8 bytes
    reason: str  # 4 bytes

    def __post_init__(self):
        Message.__post_init__(self)
        self.trading_status_message = trading_status_messages[self.status]


@dataclass
class OperationalHalt(Message):
    """
    From the TOPS specification document: "The Exchange may suspend trading of
    one or more securities on IEX for operational reasons and indicates such
    operational halt using the Operational Halt Status Message."
    """

    __slots__ = ("halt_status", "timestamp", "symbol")
    halt_status: str  # 1 byte
    timestamp: int  # 8 bytes
    symbol: str  # 8 bytes


@dataclass
class ShortSalePriceSale(Message):
    """
    From the TOPS specification document: "In association with Rule 201 of
    Regulation SHO, the Short Sale Price Test Message is used to indicate when
    a short sale price test restriction is in effect for a security."
    """

    __slots__ = ("short_sale_status", "timestamp", "symbol", "detail")
    short_sale_status: int  # 1 byte
    timestamp: int  # 8 bytes
    symbol: str  # 8 bytes
    detail: str  # 1 byte


@dataclass
class SecurityEvent(Message):
    '''
    From the DEEP specification document: "The Security Event Message is used
    to indicate events that apply to a security. A Security Event Message will
    be sent whenever such event occurs for a security"
    '''
    
    __slots__ = ('security_event','timestamp','symbol')
    security_event: int #1 byte
    timestamp: int #8 bytes
    symbol: int #8 bytes
    
@dataclass
class BidPriceLevelUpdate(Message):
    '''
    From the DEEP specificaton document: "DEEP broadcasts a real-time Price 
    Level Update Message each time a displayed price level on IEX is updated 
    during the trading day. When a price level is removed, IEX will disseminate
    a size of zero (i.e., 0x0) for the level"
    '''
    
    __slots__ = ('event_flags','timestamp','symbol','size','price_int','price')
    event_flags: int
    timestamp: int
    symbol: str
    size: int
    price_int: int
    
@dataclass
class AskPriceLevelUpdate(Message):
    '''
    From the DEEP specificaton document: "DEEP broadcasts a real-time Price 
    Level Update Message each time a displayed price level on IEX is updated 
    during the trading day. When a price level is removed, IEX will disseminate
    a size of zero (i.e., 0x0) for the level"
    '''
    
    __slots__ = ('event_flags','timestamp','symbol','size','price_int','price')
    event_flags: int
    timestamp: int
    symbol: str
    size: int
    price_int: int

@dataclass
class QuoteUpdate(Message):
    """
    From the TOPS specification document: "TOPS broadcasts a real-time Quote
    Update Message each time IEX's best bid or offer quotation is updated
    during the trading day."
    """

    __slots__ = (
        "flags",
        "timestamp",
        "symbol",
        "bid_size",
        "bid_price_int",
        "ask_price_int",
        "ask_size",
        "bid_price",
        "ask_price",
    )
    flags: int  # 1 byte
    timestamp: int  # 8 bytes
    symbol: str  # 8 bytes
    bid_size: int  # 4 bytes - Aggregate quoted best bid size
    bid_price_int: int  # 8 bytes - Best quoted bid price
    ask_price_int: int  # 8 bytes - Best quoted ask price
    ask_size: int  # 4 bytes  - Aggregate quoted best ask size


@dataclass
class TradeReport(Message):
    """
    From the TOPS specification document: "Trade Report Messages are sent when
    an order on the IEX Order Book is executed in whole or in part. TOPS sends
    a Trade Report Message for every individual fill."
    """

    __slots__ = (
        "flags",
        "timestamp",
        "symbol",
        "size",
        "price_int",
        "trade_id",
        "price",
    )
    flags: int  # 1 byte
    timestamp: int  # 8 bytes
    symbol: str  # 8 bytes
    size: int  # 4 bytes - Trade volume
    price_int: int  # 8 bytes - Trade price
    trade_id: int  # 8 bytes - Trade ID, unique within the day


@dataclass
class OfficialPrice(Message):
    """
    From the TOPS specification document: "Official Price Messages are sent for
    each IEX-listed security to indicate the IEX Official Opening Price and IEX
    Official Closing Price."
    """

    __slots__ = ("price_type", "timestamp", "symbol", "price_int", "price")
    price_type: str  # 1 byte
    timestamp: int  # 8 byte
    symbol: str  # 8 bytes
    price_int: int  # 8 bytes


@dataclass
class TradeBreak(Message):
    """
    From the TOPS specification document: "Trade Break Messages are sent when
    an execution on IEX is broken on that same trading day. Trade breaks are
    rare and only affect applications that rely upon IEX execution based data."
    """

    __slots__ = (
        "sale_flags",
        "timestamp",
        "symbol",
        "size",
        "price_int",
        "price",
        "trade_id",
    )
    sale_flags: str  # 1 byte
    timestamp: int  # 8 byte
    symbol: str  # 8 bytes
    size: int  # 4 bytes
    price_int: int  # 8 bytes
    trade_id: int  # 8 bytes


@dataclass
class AuctionInformation(Message):
    """
    From the TOPS specification document: "TOPS broadcasts an Auction
    Information Message every one second between the Lock-in Time and the
    auction match for Opening and Closing Auctions, and during the Display Only
    Period for IPO, Halt, and Volatility Auctions. Only IEX listed securities
    are eligible for IEX Auctions."
    """

    __slots__ = (
        "auction_type",
        "timestamp",
        "symbol",
        "paired_shares",
        "reference_price_int",
        "indicative_clearing_price_int",
        "imbalance_shares",
        "imbalance_side",
        "extension_number",
        "scheduled_auction_time",
        "auction_book_clearing_price_int",
        "collar_reference_price_int",
        "lower_auction_collar_price_int",
        "upper_auction_collar_price_int",
        "reference_price",
        "indicative_clearing_price",
        "auction_book_clearing_price",
        "collar_reference_price",
        "lower_auction_collar_price",
        "upper_auction_collar_price",
    )
    auction_type: str  # 1 byte
    timestamp: int  # 8 byte
    symbol: str  # 8 bytes
    # Num of shares paired at the ref price using orders on the Auction Book
    paired_shares: int  # 4 bytes
    reference_price_int: int  # 8 bytes
    # Clearing price using Eligible Auction Orders
    indicative_clearing_price_int: int  # 8 bytes
    # Num of unpaired shares at the ref price using orders on the Auction Book
    imbalance_shares: int  # 4 bytes
    imbalance_side: str  # 1 byte
    extension_number: int  # 1 byte
    scheduled_auction_time: int  # 4 bytes
    auction_book_clearing_price_int: int  # 8 bytes
    collar_reference_price_int: int  # 8 bytes
    lower_auction_collar_price_int: int  # 8 bytes
    upper_auction_collar_price_int: int  # 8 bytes


AllMessages = Union[
    ShortSalePriceSale,
    TradeBreak,
    AuctionInformation,
    TradeReport,
    OfficialPrice,
    SystemEvent,
    SecurityDirective,
    TradingStatus,
    OperationalHalt,
    QuoteUpdate,
    SecurityEvent,
    BidPriceLevelUpdate,
    AskPriceLevelUpdate
]
