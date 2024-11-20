import pytest

# Импортируем функцию
from .ai_analyzer import AIAnalyzer  # Замените `your_module` на имя вашего модуля

# Тесты для parse_response
def test_parse_response_valid_input():
    # Тест с корректным вводом
    input_data = """
    123 This is a comment
    456 Another comment
    789 Last comment
    """
    expected_output = [
        {"line": 123, "comment": "123 This is a comment"},
        {"line": 456, "comment": "456 Another comment"},
        {"line": 789, "comment": "789 Last comment"},
    ]
    assert AIAnalyzer.parse_response(input_data) == expected_output


def test_parse_response_empty_input():
    # Тест с пустой строкой
    input_data = ""
    expected_output = []
    assert AIAnalyzer.parse_response(input_data) == expected_output


def test_parse_response_none_input():
    # Тест с None
    input_data = None
    expected_output = []
    assert AIAnalyzer.parse_response(input_data) == expected_output


def test_parse_response_no_numbers():
    # Тест строки без чисел
    input_data = """
    This is a comment without number
    Another comment
    """
    expected_output = [
        {"line": 0, "comment": "This is a comment without number"},
        {"line": 0, "comment": "Another comment"},
    ]
    assert AIAnalyzer.parse_response(input_data) == expected_output


def test_parse_response_mixed_input():
    # Тест с частично корректным вводом
    input_data = """
    123 Valid comment
    Invalid comment
    456 Another valid comment
    """
    expected_output = [
        {"line": 123, "comment": "123 Valid comment"},
        {"line": 0, "comment": "Invalid comment"},
        {"line": 456, "comment": "456 Another valid comment"},
    ]
    assert AIAnalyzer.parse_response(input_data) == expected_output


def test_parse_response_whitespace_input():
    # Тест строки, состоящей только из пробелов
    input_data = "     "
    expected_output = []
    assert AIAnalyzer.parse_response(input_data) == expected_output


def test_parse_response_trailing_whitespace():
    # Тест с лишними пробелами в строках
    input_data = """
    123   Valid comment with spaces    
       456   Another comment with spaces
    """
    expected_output = [
        {"line": 123, "comment": "123   Valid comment with spaces"},
        {"line": 456, "comment": "456   Another comment with spaces"},
    ]
    assert AIAnalyzer.parse_response(input_data) == expected_output
