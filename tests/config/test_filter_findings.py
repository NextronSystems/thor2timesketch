import pytest
from pathlib import Path
from thor2timesketch.config.filter_findings import FilterFindings
from thor2timesketch.exceptions import FilterConfigError


def _write_yaml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "filters.yaml"
    p.write_text(content, encoding="utf-8")
    return p


def test_null_filter_matches_every_input():
    f = FilterFindings.null_filter()
    for lev in (None, "", "LEVEL"):
        for mod in (None, "", "MODULE"):
            assert f.matches_filter_criteria(lev, mod) is True


def test_read_filters_yaml_none_returns_null_filter():
    f = FilterFindings.read_filters_yaml(None)
    assert isinstance(f, FilterFindings)
    assert f.matches_filter_criteria("X", "Y") is True


@pytest.mark.parametrize(
    "yaml_body",
    [
        "filters: {}",  # filters key present but empty
    ],
)
def test_read_filters_yaml_empty_filters_section(tmp_path, yaml_body):
    path = _write_yaml(tmp_path, yaml_body)
    msg = f"Missing 'filters' section in filter config {path}"
    with pytest.raises(FilterConfigError) as exc:
        FilterFindings.read_filters_yaml(path)
    assert str(exc.value) == msg


@pytest.mark.parametrize(
    "levels, inc, exc",
    [
        ([], [], []),  # no includes anywhere
    ],
)
def test_read_filters_yaml_no_includes_raises(tmp_path, levels, inc, exc):
    yaml_body = f"""
filters:
  levels: {levels}
  modules:
    include: {inc}
    exclude: {exc}
  features:
    include: []
    exclude: []
"""
    path = _write_yaml(tmp_path, yaml_body)
    with pytest.raises(FilterConfigError) as exc:
        FilterFindings.read_filters_yaml(path)
    assert "Empty filter config" in str(exc.value)


def test_read_filters_yaml_levels_only(tmp_path):
    yaml_body = """
filters:
  levels:
    - Error
    - Info
  modules:
    include: []
    exclude: []
  features:
    include: []
    exclude: []
"""
    f = FilterFindings.read_filters_yaml(_write_yaml(tmp_path, yaml_body))
    assert f.matches_filter_criteria("error", None) is True
    assert f.matches_filter_criteria("INFO", "") is True
    assert f.matches_filter_criteria("warning", "any") is False


def test_read_filters_yaml_modules_only(tmp_path):
    yaml_body = """
filters:
  levels: []
  modules:
    include:
      - ModA
      - ModB
    exclude:
      - ModB
  features:
    include: []
    exclude: []
"""
    f = FilterFindings.read_filters_yaml(_write_yaml(tmp_path, yaml_body))
    assert f.matches_filter_criteria(None, "moda") is True
    assert f.matches_filter_criteria("any", "modb") is False
    assert f.matches_filter_criteria("any", "other") is False


def test_read_filters_yaml_combined_levels_and_modules(tmp_path):
    yaml_body = """
filters:
  levels:
    - Warn
  modules:
    include:
      - M1
    exclude:
      - M2
  features:
    include:
      - F1
    exclude: []
"""
    f = FilterFindings.read_filters_yaml(_write_yaml(tmp_path, yaml_body))
    # modules_final includes M1 and F1
    assert f.matches_filter_criteria("warn", "m1") is True
    assert f.matches_filter_criteria("warn", "f1") is True
    assert f.matches_filter_criteria("warn", "m2") is False
    assert f.matches_filter_criteria("info", "m1") is False


@pytest.mark.parametrize(
    "lvl,mod,expected",
    [
        ("a", None, True),
        ("A", "x", True),
        ("b", None, False),
    ],
)
def test_matches_filter_levels_only(lvl, mod, expected):
    f = FilterFindings({"A"}, set())
    assert f.matches_filter_criteria(lvl, mod) is expected


@pytest.mark.parametrize(
    "lvl,mod,expected",
    [
        (None, "m", True),
        ("x", "M", True),
    ],
)
def test_matches_filter_modules_only(lvl, mod, expected):
    f = FilterFindings(set(), {"M"})
    assert f.matches_filter_criteria(lvl, mod) is expected


@pytest.mark.parametrize(
    "lvl,mod,expected",
    [
        ("l", "m", True),
        ("l", "x", False),
        ("x", "m", False),
    ],
)
def test_matches_filter_both_filters(lvl, mod, expected):
    f = FilterFindings({"L"}, {"M"})
    assert f.matches_filter_criteria(lvl, mod) is expected


@pytest.mark.parametrize(
    "lvl,mod",
    [
        (None, None),
        ("l", None),
        (None, "m"),
        ("", ""),
    ],
)
def test_matches_filter_both_filters_none_or_empty(lvl, mod):
    f = FilterFindings({"L"}, {"M"})
    assert f.matches_filter_criteria(lvl, mod) is False
