# tests/test_get_inputs.py
from unittest.mock import patch
from datetime import datetime
import pytest
from get_inputs import get_int_input, get_nationality_code, collect_user_inputs, validate_date, NATIONALITY_CODES, countries


def test_get_int_input_valid():
    """Check for valid input"""

    with patch("builtins.input", side_effect=["10"]):
        assert get_int_input("Prompt: ", 1, 12) == 10

def test_invalid_then_valid_input():
    """Check the for input error management"""

    with patch("builtins.input", side_effect=["abc", "15", "7"]):
        assert get_int_input("Prompt: ", 1, 12) == 7

def test_input_max_attempts():
    """Check the max attempts for number of inputs"""

    with patch("builtins.input", side_effect=["13", "13", "13"]):
        with pytest.raises(ValueError):
            get_int_input("Prompt: ", 1, 12, max_attempts=3)

def is_valid_nationality_code(country):
    """Check the given nationality is within the allowed list"""

    return country in NATIONALITY_CODES

def test_valid_nationality_code(monkeypatch):
    """Check if correct nationalities are accepted"""
    
    test_input = ["UK"]
    monkeypatch.setattr("builtins.input", lambda _: test_input.pop(0))
    assert is_valid_nationality_code(*test_input)

    with patch("builtins.input", side_effect=test_input):
        assert get_nationality_code() == 826

def test_lowercase_nationality_code():
    """Check for casing when inputting nationality"""

    with patch("builtins.input", side_effect=["de"]):
        assert get_nationality_code() == 276

def test_invalid_nationality_code(monkeypatch):
    """Test for incorrect nationality"""

    test_input = ["AAAA"]
    monkeypatch.setattr("builtins.input", lambda _: test_input.pop(0))
    assert not is_valid_nationality_code(*test_input)


def test_invalid_and_valid_nationality_code():
    """Test for error management when inputting nationality"""

    with patch("builtins.input", side_effect=["xxx", "fr"]):
        assert get_nationality_code() == 250

def test_valid_collect_user_inputs(monkeypatch):
    """Check for a complete set of inputs"""

    test_inputs = ["2000", "5", "20", "2030", "8", "UK"]
    monkeypatch.setattr("builtins.input", lambda _: test_inputs.pop(0))

    result = collect_user_inputs()
    assert result["birth_year"] == 2000
    assert result["current_year"] == 2025

def test_invalid_birthday(monkeypatch):
    """Check for acceptable dates for DOB"""
    test_inputs = [2001, 2, 30]
    monkeypatch.setattr("builtins.input", lambda _: test_inputs.pop(0))

    assert validate_date(*test_inputs) == False


    

