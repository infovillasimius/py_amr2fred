import unittest
from unittest.mock import patch, mock_open

from glossary import Glossary
from node import Node
from propbank import Propbank


class TestPropbank(unittest.TestCase):

    def setUp(self):
        """Initialize a Propbank instance."""
        self.propbank = Propbank.get_propbank()

    @patch("builtins.open", new_callable=mock_open, read_data="header1\theader2\nword1\tvalue1\nword2\tvalue2")
    @patch("csv.reader", return_value=[["header1", "header2"], ["word1", "value1"], ["word2", "value2"]])
    def test_file_read(self, mock_csv_reader, mock_open_file):
        """Test file_read method."""
        result = Propbank.file_read("fake_file.tsv")
        expected_header = ["header1", "header2"]
        expected_rows = [["word1", "value1"], ["word2", "value2"]]

        self.assertEqual(result[0], expected_header)
        self.assertEqual(result[1], expected_rows)

    def test_get_propbank(self):
        """Test singleton behavior of get_propbank."""
        propbank_1 = Propbank.get_propbank()
        propbank_2 = Propbank.get_propbank()
        self.assertIs(propbank_1, propbank_2)

    def test_frame_find(self):
        """Test frame_find method."""
        word = "pbrs:1500-01"
        field = Glossary.PropbankFrameFields.PB_Frame
        result = self.propbank.frame_find(word, field)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], word)

    def test_role_find(self):
        """Test role_find method."""
        word = "pbrs:1500-01"
        value = "pblr:1500-01.thing-that-is-1500"
        role_field = Glossary.PropbankRoleFields(0)  # Assuming first column
        role_field_2 = Glossary.PropbankRoleFields(1)  # Assuming second column

        result = self.propbank.role_find(word, role_field, value, role_field_2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0:2], ["pbrs:1500-01", "pblr:1500-01.thing-that-is-1500"])

    def test_list_find(self):
        """Test list_find method."""
        word = "pbrs:1500-01"
        node = Node(var="z1", relation=":ARG1")
        args = [node]

        result = self.propbank.list_find(word, args)

        self.assertIsNotNone(result)
        self.assertEqual(result[0][0], "pbrs:1500-01")


if __name__ == "__main__":
    unittest.main()
