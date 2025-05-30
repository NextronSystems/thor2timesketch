from typer.testing import CliRunner
from thor2timesketch.cli.controller import app

runner = CliRunner()


def test_help_flag():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Convert THOR security scanner logs" in result.stdout


def test_version_flag(monkeypatch):
    # force a known version
    monkeypatch.setenv("PYTHONPATH", ".")
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "thor2timesketch version" in result.stdout


def test_missing_input_file(tmp_path):
    missing = tmp_path / "nope.json"
    result = runner.invoke(app, [str(missing)])
    assert result.exit_code == 1
    assert "Input file not found" in result.stdout


def test_require_output_or_sketch(tmp_path):
    # create a dummy input file
    input_file = tmp_path / "data.json"
    input_file.write_text("[]")
    result = runner.invoke(app, [str(input_file)])
    assert result.exit_code == 1
    assert "Use -o/--output for file output or --sketch" in result.stdout
