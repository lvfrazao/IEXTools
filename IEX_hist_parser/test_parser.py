import unittest
from . import IEXparser


class ParserTestCases(unittest.TestCase):
    """
    Tests for parser.py
    """
    def test_file_load(self):
        """
        Tests the functionality of the records file reader for normal
        functionality (loads a file and doesn't raise an exception)
        """
        test_file = 'input_files\\example1.pcap'
        p = IEXparser.Parser(test_file)

        self.assertEqual(
            1,
            1,
            msg=f'Test with {test_file}'
        )

    def test_seek_header(self):
        """
        Tests functions ability to find the TP header
        """
        test_file = 'input_files\\example1.pcap'

        p = IEXparser.Parser(test_file)
        p._seek_header()

        self.assertEqual(p.bytes_read, 1930)
    
    def test_end_to_end(self):
        test_file = 'input_files\\example1.pcap'
        with IEXparser.Parser(test_file) as p:
            for message in p:
                pass


if __name__ == '__main__':
    unittest.main()
