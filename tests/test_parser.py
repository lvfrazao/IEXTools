import unittest
import parser


class ParserTestCases(unittest.TestCase):
    """
    Tests for parser.py
    """
    def test_file_load(self):
        """
        Tests the functionality of the records file reader for normal
        functionality (file as expected)
        """
        test_file = 'input_files\\example1.pcap'

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

        p = parser.Parser(test_file)
        p._seek_header()

        self.assertEqual(p.bytes_read, 1902)


if __name__ == '__main__':
    unittest.main()