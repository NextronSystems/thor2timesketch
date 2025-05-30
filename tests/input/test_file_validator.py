import pytest
from pathlib import Path
from thor2timesketch.input.file_validator import FileValidator
from thor2timesketch.exceptions import (
    FileNotFound,
    FileNotReadableError,
    EmptyFileError,
    InvalidFileExtensionError,
)


@pytest.fixture
def validator():
    return FileValidator(valid_extensions=[".json", ".jsonl", ".yml", ".yaml"])


def test_valid_file(tmp_path, validator):
    test_file = tmp_path / "sample.json"
    test_file.write_text("dummy content")
    assert validator.validate_file(test_file) == test_file


def test_file_not_readable(tmp_path, validator, monkeypatch):
    test_file = tmp_path / "unreadable.json"
    test_file.write_text("content")
    monkeypatch.setattr(
        Path, "open", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("denied"))
    )
    with pytest.raises(FileNotReadableError):
        validator.validate_file(test_file)


@pytest.mark.parametrize(
    "filename, content, expected_exc",
    [
        ("nonexistent.json", None, FileNotFound),
        ("empty.json", "", EmptyFileError),
        ("invalid.txt", "x", InvalidFileExtensionError),
    ],
)
def test_invalid_file_cases(tmp_path, filename, content, expected_exc, validator):
    file_path = tmp_path / filename
    if content is not None:
        file_path.write_text(content)
    with pytest.raises(expected_exc):
        validator.validate_file(file_path)
