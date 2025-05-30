from typing import Optional
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.config.yaml_config_reader import YamlConfigReader
from thor2timesketch.constants import YAML_FILTERS
from thor2timesketch.exceptions import FilterConfigError
from pathlib import Path


class FilterFindings:
    def __init__(self, levels: set[str], modules: set[str]) -> None:
        self._levels = {level.lower() for level in levels}
        self._modules = {module.lower() for module in modules}
        ConsoleConfig.debug(
            f"Filter initialized with levels={levels}, modules={modules}"
        )

    @classmethod
    def read_filters_yaml(
        cls, config_filter: Optional[Path] = None
    ) -> "FilterFindings":

        if config_filter is None:
            return cls.null_filter()

        filters = YamlConfigReader.load_yaml(config_filter)
        filter_section = filters.get(YAML_FILTERS)

        if not filter_section:
            raise FilterConfigError(
                f"Missing 'filters' section in filter config {config_filter}"
            )

        levels = {
            level.lower()
            for level in filter_section.get("levels") or {}
            if isinstance(level, str)
        }
        modules = filter_section.get("modules", {}) or {}
        modules_include = {
            module.lower()
            for module in modules.get("include", [])
            if isinstance(module, str)
        }
        modules_exclude = {
            module.lower()
            for module in modules.get("exclude", [])
            if isinstance(module, str)
        }
        features = filter_section.get("features", {}) or {}
        features_include = {
            feature.lower()
            for feature in features.get("include", [])
            if isinstance(feature, str)
        }
        features_exclude = {
            feature.lower()
            for feature in features.get("exclude", []) or []
            if isinstance(feature, str)
        }

        modules_filtered = modules_include - modules_exclude
        features_filtered = features_include - features_exclude
        modules_final = modules_filtered | features_filtered

        if not levels and not modules_final:
            raise FilterConfigError(
                f"Empty filter config in {config_filter}: at least one filter include (levels or modules) must be provided"
            )
        ConsoleConfig.info(
            f"Filter config loaded from {config_filter}: levels={levels}, modules={modules_final}"
        )
        return cls(levels, modules_final)

    @classmethod
    def null_filter(cls) -> "FilterFindings":
        return _NullFilterFindings(set(), set())

    def matches_filter_criteria(
        self, level: Optional[str], module: Optional[str]
    ) -> bool:
        norm_level = level.lower() if level is not None else None
        norm_module = module.lower() if module is not None else None
        if self._levels and not self._modules:
            return norm_level in self._levels
        if self._modules and not self._levels:
            return norm_module in self._modules
        return norm_level in self._levels and norm_module in self._modules


class _NullFilterFindings(FilterFindings):
    def matches_filter_criteria(
        self, level: Optional[str], module: Optional[str]
    ) -> bool:
        return True
