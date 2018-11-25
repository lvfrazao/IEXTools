"""
Unittests for the parser class.

To run unittest you must use the unittest module's cli due to Python's import
system:

Go into the top level directory and run the command:
py -m unittest IEXTools.tests.test_parser
"""
import os
import sys
import unittest
from IEXTools import IEXparser as iex


file_path = "IEXTools\\tests\\input_files\\example1.pcap"


class ParserTestCases(unittest.TestCase):
    """
    Tests for IEXparser.py
    """

    def setUp(self):
        self.test_file = file_path
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
        test_file = file_path
        with iex.Parser(test_file) as p:
            for message in p:
                pass


if __name__ == "__main__":
    unittest.main()
