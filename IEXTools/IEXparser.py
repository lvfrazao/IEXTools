"""
IEXparser.py

Purpose:
This module contains the 'Parser' class which scans the IEX pcap file,
identifies messages and decodes them using the struct module.

Usage:
To create a Parser object simply supply the file path as an argument

> iex_parser = Parser('c:\\example.pcap')

This instantiates a Parser object with the pcap file opened. You can also
optionally specify what type of HIST file you are loading, either TOPS
(`tops=True`) or DEEP (`deep=True`).

Use the `get_next_message` method of the Parser object to return a message
object. The message objects are documented in the messages.py module.

> new_message = iex_parser.get_next_message()

The last message retrieved can also be accessed through the Parser object
itself with the `message` attribute. Similarly the message type can be accessed
as `Parser.message_type` and the binary encoded message can be accessed with
`Parser.message_binary`.

Benchmarks:
'''
Beginning test - 1,000,000 messages - all messages, not printing
Parsed 1,000,000 messages in 52.2 seconds -- 19141.6 messages per second
------------------------------------------------------------------------
Beginning test - 1,000,000 messages - only TradeReport and QuoteUpdate
messages, not printing
Parsed 1,000,000 messages in 54.0 seconds -- 18512.9 messages per second
'''
"""
from __future__ import annotations
from datetime import datetime, timezone
import gzip
import struct
from . import messages
from typing import BinaryIO, Optional, Iterator, Union, List, Tuple, Dict
from .IEXHISTExceptions import ProtocolException
from .messages import AllMessages


class Parser(object):
    """
    Creates the Parser object. Simply pass the filepath of the pcap file when
    initializing the object.

    Usage:
    p = Parser(filepath)
    """

    def __init__(
        self,
        file_path: str,
        tops: bool = True,
        deep: bool = False,
        version: float = 1.6,
    ) -> None:
        if isinstance(file_path,str):
            self.file_path = file_path
            self.file = self._load(file_path)
        else:
            self.file=file_path
            self.file_path=file_path.filename
            
        self.tops = tops
        self.deep = deep
        # IEX TP Header Structure
        # Many of these byte strings are hardcoded and may cause compatibility
        # issues with future or previous versions of TOPS, DEEP, or the EIX
        # Transport Protocol
        self.version = b"\x01"
        self.reserved = b"\x00"
        if tops and not deep:
            protcol_ids = {1.5: b"\x02\x80", 1.6: b"\x03\x80"}
            self.protocol_id = protcol_ids[version]
        elif deep:
            self.protocol_id = b"\x04\x80"
            version=1.0
#            raise NotImplementedError("Parsing of DEEP files not implemented")
        elif deep and tops:
            raise ValueError('"deep" and "tops" arguments cannot both be true')
        self.channel_id = b"\x01\x00\x00\x00"
        self.session_id = self._get_session_id(self.file)
        self.file.seek(0)
        self.tp_header = (
            self.version
            + self.reserved
            + self.protocol_id
            + self.channel_id
            + self.session_id
        )
        self.messages_left = 0
        self.bytes_read = 0

        self.messages_types: Dict[AllMessages, bytes] = {
            messages.ShortSalePriceSale: b"\x50",
            messages.TradeBreak: b"\x42",
            messages.AuctionInformation: b"\x41",
            messages.TradeReport: b"\x54",
            messages.OfficialPrice: b"\x58",
            messages.SystemEvent: b"\x53",
            messages.SecurityDirective: b"\x44",
            messages.TradingStatus: b"\x48",
            messages.OperationalHalt: b"\x4f",
            messages.QuoteUpdate: b"\x51",
            messages.SecurityEvent: b'\x45',
            messages.BidPriceLevelUpdate: b'\x38',
            messages.AskPriceLevelUpdate: b'\x35'
        }

        self.decoder = messages.MessageDecoder(version=version)

    def __repr__(self) -> str:
        return f'Parser("{self.file_path}", tops={self.tops}, deep={self.deep})'

    def __iter__(self) -> Iterator:
        return self

    def __next__(self) -> AllMessages:
        """
        Meant to allow the user to use the Parser object in a loop to read
        through all messages in a pcap file similar to reading all lines in a
        file.

        Usage:
        for message in Parser(file_path):
            do_something(message)
        """
        return self.get_next_message()

    def __enter__(self) -> Parser:
        return self

    def __exit__(self, *args) -> None:
        self.file.close()

    def _load(self, file_path: str) -> BinaryIO:
        """
        Function to load a TOPS File into the parser. Simply returns a file
        object which other methods will iterate over.
        """
        if file_path.endswith('.gz'):
            return gzip.open(file_path, "rb")
        else:
            return open(file_path, "rb")

    def _get_session_id(self, market_file: BinaryIO) -> bytes:
        """
        The session ID is unique every day. Simply denotes the day. We use this
        to build the IEX Transport Protocol header.

        inputs:

            file_path   : path to pcap file to be decoded

        Returns:

            session_id  : binary encoded session ID
        """
        try:
            return self.session_id
        except AttributeError:
            iex_header_start = (
                self.version + self.reserved + self.protocol_id + self.channel_id
            )
            print(iex_header_start)
            found = False
            i = 0
            while not found:
                cur_chunk = market_file.read(1)
                if cur_chunk[0] == iex_header_start[i]:
                    i += 1
                    if i == len(iex_header_start):
                        found = True
                else:
                    i = 0

            if found:
                return market_file.read(4)
        raise ProtocolException("Session ID could not be found in the supplied file")

    def read_next_line(self) -> bytes:
        """
        Reads one line of the open pcap file, captures the len of that line,
        and returns that line to the caller. Not very useful to be honest, this
        may be deprecated in future versions.

        Inputs:

            None

        Returns:

            line    : binary encoded line from the pcap file
        """
        line = self.file.readline()
        self.bytes_read += len(line)
        if line:
            return line
        else:
            raise StopIteration("Reached end of PCAP file")

    def read_chunk(self, chunk: int = 1024) -> bytes:
        """
        Reads a single chunk of arbitrary size from the open file object and
        returns that chunk to the caller.

        Inputs:

            chunk   : determines the chunk size to be read from file

        Returns:

            data    : binary encoded chunk from the pcap file
        """
        data = self.file.read(chunk)
        self.bytes_read += len(data)
        if data:
            return data
        else:
            raise StopIteration("Reached end of PCAP file")

    def _seek_header(self) -> None:
        """
        Scans through the open file until it finds a complete version of the
        Transport Protocol Header which means that there is at least one
        message to parse.
        """
        found = False
        target_i = len(self.tp_header)
        i = 0
        while not found:
            cur_chunk = self.read_chunk(1)
            if cur_chunk[0] == self.tp_header[i]:
                i += 1
                if i == target_i:
                    found = True
            else:
                i = 0
        header_fmt = "<hhqqq"
        remaining_header = struct.unpack(header_fmt, self.read_chunk(28))
        self.cur_msg_payload_len = remaining_header[0]
        self.messages_left = remaining_header[1]
        self.cur_stream_offset = remaining_header[2]
        self.first_sequence_number = remaining_header[3]
        self.cur_send_time = datetime.fromtimestamp(
            remaining_header[4] / 10 ** 9, tz=timezone.utc
        )

    def get_next_message(
        self, allowed: Optional[Union[List[AllMessages], Tuple[AllMessages]]] = None
    ) -> AllMessages:
        """
        Returns the next message in the pcap file. The user may optionally
        provide an 'allowed' argument to specify which type of messages they
        would like to retrieve. Please note that limiting the returned messages
        probably does not improve performance by that much, in fact tests have
        shown reduced rate of messages returned when allowed messages are
        specified (note the rate of messages returned is lower, but not the
        rate of messages analyzed).

        Inputs:

            allowed : types of messages to be returned

        Returns:

            message : decoded message from IEX file
        """
        if not isinstance(allowed, (list, tuple)) and allowed is not None:
            raise ValueError("allowed must be either a list or tuple")
        if allowed:
            allowed_types = [self.messages_types[a][0] for a in allowed]

        while not self.messages_left:
            self._seek_header()

        self._read_next_message()
        while allowed is not None and self.message_type not in allowed_types:
            while not self.messages_left:
                self._seek_header()

            self._read_next_message()

        self.message = self.decoder.decode_message(
            self.message_type, self.message_binary
        )
        return self.message

    def _read_next_message(self) -> None:
        """
        Read next message from file - no return value, works by side effect.

        Note: using seek() to move past messages that we dont want to read
        doesn't seem to help performance. My theory is that using mmap should
        not help much either given that were typically reading the files from
        beginning to end sequentially.
        """
        message_len = struct.unpack("<h", self.read_chunk(2))[0]
        self.messages_left -= 1
        self.message_type = self.read_chunk(1)[0]
        self.message_binary = self.read_chunk(message_len - 1)
