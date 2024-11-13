import unittest
from auto_code_review.ai_analyzer import AIAnalyzer

class TestParseResponse(unittest.TestCase):
    def test_valid_response(self):
        # Test correct response
        analysis = [
            "1. Line 1: Changed 'foo' to 'bar'.",
            "2. Line 2: Removed unnecessary print statement.",
            "3. Line 5: Updated variable name from 'x' to 'y'."
        ]
        expected_comments = [
            (1, "Changed 'foo' to 'bar'."),
            (2, "Removed unnecessary print statement."),
            (5, "Updated variable name from 'x' to 'y'.")
        ]
        result = AIAnalyzer.parse_response(analysis)
        self.assertEqual(result, expected_comments)

    def test_empty_response(self):
        # Test empty response
        analysis = []
        expected_comments = []
        result = AIAnalyzer.parse_response(analysis)
        self.assertEqual(result, expected_comments)

    def test_malformed_response(self):
        # Test invalid response format
        analysis = [
            "1. Line one: This should be ignored.",
            "Line 2 This is missing a colon.",
            "Line 3: Correct format comment."
        ]
        expected_comments = [
            (3, "Correct format comment.")
        ]
        result = AIAnalyzer.parse_response(analysis)
        self.assertEqual(result, expected_comments)

    def test_non_integer_line_number(self):
        # Тest case when line number is not actually a number
        analysis = [
            "1. Line abc: This line should be ignored.",
            "2. Line 4: This line is valid."
        ]
        expected_comments = [
            (4, "This line is valid.")
        ]
        result = AIAnalyzer.parse_response(analysis)
        self.assertEqual(result, expected_comments)

if __name__ == "__main__":
    unittest.main()
