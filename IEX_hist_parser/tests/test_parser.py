import os
import sys
import unittest
import IEX_hist_parser.IEXparser as iex

if sys.argv[0]:
    os.chdir(os.path.dirname(sys.argv[0]))


class ParserTestCases(unittest.TestCase):
    """
    Tests for parser.py
    """

    def setUp(self):
        self.test_file = "input_files\\example1.pcap"
        self.p = iex.Parser(self.test_file)

    def tearDown(self):
        self.p.file.close()

    def test_file_load(self):
        """
        Tests the functionality of the records file reader for normal
        functionality (loads a file and doesn't raise an exception)
        """

        self.assertEqual(1, 1, msg=f"Test with {self.test_file}")

    def test_seek_header(self):
        """
        Tests functions ability to find the TP header
        """
        self.p._seek_header()

        self.assertEqual(self.p.bytes_read, 1930)

    def test_end_to_end(self):
        test_file = "input_files\\example1.pcap"
        with iex.Parser(test_file) as p:
            for message in p:
                pass


if __name__ == "__main__":
    unittest.main()
