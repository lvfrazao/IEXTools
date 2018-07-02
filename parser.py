"""
IEX_parser.py

Purpose:
This module contains the 'Parser' class which scans the IEX pcap file,
identifies messages and decodes them using the struct module.

Usage:
To create a Parser object simply supply the file path as an argument
$ historical_data = Parser('c:\\example.pcap')
"""
import struct
from datetime import datetime, timezone


fmt = {
    'short_int': 'h'
}


class Parser(object):
    def __init__(self, file_path, tops=True, deep=False):
        self.file = self._load(file_path)
        # IEX TP Header Structure
        self.version = b'\x01'
        self.reserved = b'\x00'
        if tops and not deep:
            self.protocol_id = b'\x03\x80'
        elif deep:
            self.protocol_id = b'\x04\x80'
            raise NotImplementedError('Parsing of DEEP files not implemented')
        elif deep and tops:
            raise ValueError('"deep" and "tops" arguments cannot both be true')
        self.channel_id = b'\x01\x00\x00\x00'
        self.session_id = self._get_session_id(file_path)
        self.tp_header = (
            self.version +
            self.reserved +
            self.protocol_id +
            self.channel_id +
            self.session_id
            )
        self.messages_left = 0
        self.bytes_read = 0

    def _load(self, file_path):
        """
        Function to load a TOPS File into the parser. Simply returns a file
        object which other methods will iterate over.
        """
        return open(file_path, 'rb')

    def _get_session_id(self, file_path):
        """
        The session ID is unique every day. Simply denotes the day. We use this
        to build the IEX Transport Protocol header.
        """
        try:
            return self.session_id
        except AttributeError:
            iex_header_start = (
                self.version +
                self.reserved +
                self.protocol_id +
                self.channel_id
            )
            with open(file_path, 'rb') as market_file:
                for line in market_file:
                    if iex_header_start in line:
                        line = line.split(iex_header_start)[1]
                        return line[:4]

    def read_next_line(self):
        """
        Reads one line of the open pcap file, captures the len of that line,
        and returns that line to the caller
        """
        line = self.file.readline()
        self.bytes_read += len(line)
        return line

    def read_chunk(self, chunk=1024):
        """
        Reads a single chunk of arbitrary size from the open file object and
        returns that chunk to the caller
        """
        self.bytes_read += chunk
        return self.file.read(chunk)

    def _seek_header(self):
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
        remaining_header = struct.unpack('<hhqqq', self.read_chunk(28))
        self.cur_msg_payload_len = remaining_header[0]
        self.messages_left = remaining_header[1]
        self.cur_stream_offset = remaining_header[2]
        self.first_sequence_number = remaining_header[3]
        self.cur_send_time = datetime.fromtimestamp(
            remaining_header[4] / 10**9,
            tz=timezone.utc
        )

    def get_next_message(self):
        if self.messages_left:
            # Read next message
            message_len = struct.unpack('<h', self.read_chunk(2))[0]
            message = self.read_chunk(message_len)
            message_type = message[0]
        else:
            # If no messages left from current packet find the next TP header
            self._seek_header()
            return self.get_next_message()

    def _get_payload_length(file_path):
        pass


if __name__ == '__main__':
    file_path = r'C:\Users\luiz_\Dropbox\Personal\Python\Programs\IEX_hist_parser\IEX TOPS Sample\20180103_IEXTP1_TOPS1.6.pcap'
    p = Parser(file_path)
    p._seek_header()
    print(p.bytes_read)
