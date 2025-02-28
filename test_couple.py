import unittest

from couple import Couple


class TestCouple(unittest.TestCase):

    def setUp(self):
        """Create a sample Couple instance for testing."""
        self.couple = Couple(occurrence=5, word="example")

    def test_initialization(self):
        """Test Couple initialization."""
        self.assertEqual(self.couple.get_word(), "example")
        self.assertEqual(self.couple.get_occurrence(), 5)

    def test_string_representation(self):
        """Test __str__ method."""
        expected_str = "\nWord: example - occurrences: 5"
        self.assertEqual(str(self.couple), expected_str)

    def test_get_word(self):
        """Test get_word method."""
        self.assertEqual(self.couple.get_word(), "example")

    def test_get_occurrence(self):
        """Test get_occurrence method."""
        self.assertEqual(self.couple.get_occurrence(), 5)

    def test_set_occurrence(self):
        """Test set_occurrence method."""
        self.couple.set_occurrence(10)
        self.assertEqual(self.couple.get_occurrence(), 10)

    def test_increment_occurrence(self):
        """Test increment_occurrence method."""
        self.couple.increment_occurrence()
        self.assertEqual(self.couple.get_occurrence(), 6)


if __name__ == "__main__":
    unittest.main()
