import unittest
from gui import has_cleanliness_keywords


class TestHasCleanlinessKeywords(unittest.TestCase):

    def test_has_cleanliness_keywords_positive(self):
        comment = "The room was very clean and tidy."
        self.assertTrue(has_cleanliness_keywords(comment))

    def test_has_cleanliness_keywords_negative(self):
        comment = "The room was very spacious and bright."
        self.assertFalse(has_cleanliness_keywords(comment))

    def test_has_cleanliness_keywords_non_string_input(self):
        comment = 12345  # non-string input
        self.assertFalse(has_cleanliness_keywords(comment))

    def test_has_cleanliness_keywords_empty_string(self):
        comment = ""  # empty string
        self.assertFalse(has_cleanliness_keywords(comment))

if __name__ == "__main__":
    unittest.main()
