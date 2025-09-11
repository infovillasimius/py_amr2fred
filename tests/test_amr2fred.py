import unittest
from unittest.mock import patch

from rdflib import Graph

from py_amr2fred.amr2fred import Amr2fred
from py_amr2fred.glossary import Glossary
from py_amr2fred.rdf_writer import RdfWriter


class TestAmr2fred(unittest.TestCase):

    def setUp(self):
        """Initialize an Amr2fred instance."""
        self.amr2fred = Amr2fred()

    @patch("requests.get")
    def test_get_amr_spring(self, mock_get):
        """Test get_amr with the default Spring API."""
        mock_get.return_value.text = '{"penman": "(a / example)"}'
        result = self.amr2fred.get_amr("example sentence", alt_api=False, multilingual=False)

        self.assertEqual(result, "(a / example)")
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_amr_alt_spring(self, mock_get):
        """Test get_amr with the alternative Spring API."""
        mock_get.return_value.text = '{"penman": "(b / test)"}'
        result = self.amr2fred.get_amr("test sentence", alt_api=True, multilingual=False)

        self.assertEqual(result, "(b / test)")
        mock_get.assert_called_once()

    @patch("requests.post")
    def test_get_amr_usea(self, mock_post):
        """Test get_amr with the multilingual Usea API."""
        mock_post.return_value.text = '{"amr_graph": "(c / multilingual-example)"}'
        result = self.amr2fred.get_amr("multilingual sentence", alt_api=False, multilingual=True)

        self.assertEqual(result, "(c / multilingual-example)")
        mock_post.assert_called_once()

    @patch.object(Amr2fred, "get_amr", return_value="(d / test-amr)")
    @patch.object(Glossary, "FRED_NS", "http://example.org/fred#")
    @patch("py_amr2fred.rdf_writer.RdfWriter.to_rdf")
    @patch("py_amr2fred.rdf_writer.RdfWriter.serialize", return_value="<rdf serialization>")
    def test_translate(self, mock_get_amr, mock_to_rdf, mock_serialize):
        """Test translate method with serialization."""

        result = self.amr2fred.translate(text="test sentence", serialize=True, post_processing=False)

        self.assertEqual(result, "<rdf serialization>")
        mock_get_amr.assert_called_once()
        mock_to_rdf.assert_called_once()
        mock_serialize.assert_called_once()

    @patch.object(Amr2fred, "get_amr", return_value="(e / test-amr)")
    @patch("py_amr2fred.rdf_writer.RdfWriter.to_rdf")
    def test_translate_graph_output(self, mock_to_rdf, mock_get_amr):
        """Test translate method without serialization (Graph output)."""

        result = self.amr2fred.translate(text="test sentence", serialize=False, post_processing=False)

        self.assertIsInstance(result, Graph)
        mock_get_amr.assert_called_once()
        mock_to_rdf.assert_called_once()

    def test_translate_no_input(self):
        """Test translate with no input arguments."""
        result = self.amr2fred.translate()
        self.assertEqual(result, "Nothing to do!")

    @patch("logging.Logger.warning")
    @patch("requests.get", side_effect=Exception("API error"))
    def test_get_amr_exception_handling(self, mock_get, mock_logger):
        """Test get_amr handles API errors gracefully."""
        result = self.amr2fred.get_amr("error sentence", alt_api=False, multilingual=False)

        self.assertIsNone(result)
        mock_logger.assert_called()  # Ensures a warning was logged
        mock_logger.assert_any_call("API error")  # Checks for string message, not an exception object


if __name__ == "__main__":
    unittest.main()
