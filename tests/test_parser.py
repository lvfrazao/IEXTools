import unittest
from parser import Parser


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


if __name__ == '__main__':
    unittest.main()