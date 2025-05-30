import pytest
from pathlib import Path
from thor2timesketch.input.json_reader import JsonReader
from thor2timesketch.exceptions import JsonParseError, InputError


@pytest.fixture(autouse=True)
def skip_file_validation(monkeypatch):
    monkeypatch.setattr(JsonReader, "_validate_file", lambda self, f: Path(f))


@pytest.fixture
def reader():
    return JsonReader()


def test_read_multiple_json_lines_and_skip_blanks(tmp_path, reader):
    file_path = tmp_path / "data.json"
    file_path.write_text('{"a": 1}\n' "\n" '{"b": 2}\n' "   \n" '{"c": 3}\n')
    result = list(reader.get_valid_data(file_path))
    assert result == [{"a": 1}, {"b": 2}, {"c": 3}]


def test_partial_yield_then_error(tmp_path, reader):
    file_path = tmp_path / "mixed.json"
    file_path.write_text('{"ok": 1}\n' "{bad json}\n" '{"never": "reached"}\n')
    it = reader.get_valid_data(file_path)
    assert next(it) == {"ok": 1}
    with pytest.raises(JsonParseError):
        next(it)


def test_input_error_on_file_read(tmp_path, reader, monkeypatch):
    file_path = tmp_path / "exists.json"
    file_path.write_text('{"x": 1}\n')
    monkeypatch.setattr(
        Path, "open", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("fail"))
    )
    with pytest.raises(InputError):
        list(reader.get_valid_data(file_path))
