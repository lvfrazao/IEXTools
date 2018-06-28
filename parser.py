# IEX_parser.py
import struct


class Parser(object):
    def __init__(self, file_path, tops=True, deep=False):
        self.file = self._load(file_path)
        # IEX TP Header Structure
        self.version = b'\x01'
        self.reserved = b'\x00'
        if tops:
            self.protocol_id = b'\x03\x80'
        elif deep:
            self.protocol_id = b'\x04\x80'
            raise NotImplementedError('Parsing of DEEP files not implemented')
        elif deep and tops:
            raise ValueError('"deep" and "tops" arguments cannot both be true')
        self.channel_id = b'\x01\x00\x00\x00'
        self.session_id = self.get_session_id()
        self.tp_header = (
            self.version +
            self.reserved +
            self.protocol_id +
            self.channel_id +
            self.session_id
            )

    def _load(self, file_path):
        """
        Function to load a TOPS File into the parser
        """
        return open(file_path, 'rb')

    def read_next_line(self):
        return self.file.readline()

    def read_chunk(self, chunk=1024):
        return self.file.read(chunk)

    def get_next_message(self):
        pass

    def get_session_id(self, ):
        try:
            return self.session_id
        except NameError:
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

    def get_payload_length(file_path):
        with open(file_path, 'rb') as market_file:
            for line in market_file:
                if iex_header_start in line:
                    line = line.split(iex_header_start)[1]
                    return line[4:6]
