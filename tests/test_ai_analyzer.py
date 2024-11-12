import unittest
from unittest.mock import patch
from auto_code_review.ai_analyzer import AIAnalyzer

class TestAIAnalyzer(unittest.TestCase):
    def setUp(self):
        self.api_key = "fake_api_key"
        self.settings = {
            "temperature": 0.5,
            "max_tokens": 500,
            "ai_model": "gpt-4o-mini"
        }
        self.analyzer = AIAnalyzer(self.api_key, self.settings)
        self.diff = "@@ -1,3 +1,3 @@\n- old line\n+ new line with error\n"

    @patch("openai.ChatCompletion.create")
    def test_analyze_diff(self, mock_create):
        # Мокаем ответ OpenAI API
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Line 1: Consider fixing the typo 'error'."
                    }
                }
            ]
        }
        mock_create.return_value = mock_response

        # Тестируем метод analyze_diff
        comments = self.analyzer.analyze_diff(self.diff)

        # Проверяем результат
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0], (1, "Consider fixing the typo 'error'."))

    @patch("openai.ChatCompletion.create")
    def test_analyze_diff_no_comments(self, mock_create):
        # Мокаем ответ, когда комментарии не требуются
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": ""
                    }
                }
            ]
        }
        mock_create.return_value = mock_response

        comments = self.analyzer.analyze_diff(self.diff)
        self.assertEqual(comments, [])

    @patch("openai.ChatCompletion.create")
    def test_analyze_diff_invalid_response_format(self, mock_create):
        # Мокаем ответ с некорректным форматом
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "This is not a valid response format."
                    }
                }
            ]
        }
        mock_create.return_value = mock_response

        comments = self.analyzer.analyze_diff(self.diff)
        self.assertEqual(comments, [])

if __name__ == "__main__":
    unittest.main()
