import pytest
from thor2timesketch.input.json_validator import JsonValidator
from thor2timesketch.exceptions import JsonParseError, JsonValidationError


@pytest.fixture
def validator():
    return JsonValidator()


def test_empty_or_whitespace_line_returns_none(validator):
    assert validator.validate_json_log("") is None
    assert validator.validate_json_log("   \t\n") is None


def test_valid_json_returns_dict(validator):
    obj = validator.validate_json_log('{"key": "value", "n": 1}')
    assert isinstance(obj, dict)
    assert obj == {"key": "value", "n": 1}


def test_invalid_json_raises_parse_error(validator):
    with pytest.raises(JsonParseError):
        validator.validate_json_log("{not: valid json}")


def test_non_dict_json_raises_validation_error(validator):
    with pytest.raises(JsonValidationError):
        validator.validate_json_log("[1, 2, 3]")
