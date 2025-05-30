from typing import Optional, Set, Any
from pathlib import Path
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.config.yaml_config_reader import YamlConfigReader
from thor2timesketch.constants import (
    AUDIT_INFO,
    AUDIT_FINDING,
    AUDIT_TRAIL,
    YAML_FILTERS,
)
from thor2timesketch.exceptions import FilterConfigError


class FilterAudit:

    def __init__(self, audit_trail: Set[str]) -> None:
        self._allowed_filters = {select.lower() for select in audit_trail}
        ConsoleConfig.debug(
            f"Audit trail filter initialized with types={self._allowed_filters}"
        )

    @classmethod
    def read_audit_yaml(cls, config_path: Optional[Path]) -> "FilterAudit":
        if not config_path:
            return cls.null_filter()

        filters = YamlConfigReader.load_yaml(config_path)
        filter_section = filters.get(YAML_FILTERS)
        if not filter_section:
            raise FilterConfigError(
                f"Missing '{YAML_FILTERS}' section in filter config {config_path}"
            )
        audit_trail_filters = filter_section.get(AUDIT_TRAIL, [])
        allowed_filters = set(audit_trail_filters)
        if not allowed_filters:
            allowed_filters = {AUDIT_INFO, AUDIT_FINDING}
        return cls(allowed_filters)

    @classmethod
    def null_filter(cls) -> "FilterAudit":
        return cls({AUDIT_INFO.lower(), AUDIT_FINDING.lower()})

    def get_audit_trail_selector(self, audit_json: dict[str, Any]) -> Optional[str]:

        has_findings = AUDIT_FINDING in audit_json and isinstance(
            audit_json[AUDIT_FINDING], list
        )
        has_info = AUDIT_INFO in audit_json and isinstance(audit_json[AUDIT_INFO], dict)

        if (
            AUDIT_FINDING in self._allowed_filters
            and AUDIT_INFO in self._allowed_filters
        ):
            if has_findings:
                return AUDIT_FINDING
            if has_info:
                return AUDIT_INFO
            return None
        if AUDIT_INFO in self._allowed_filters and has_info:
            return AUDIT_INFO
        if AUDIT_FINDING in self._allowed_filters and has_findings:
            return AUDIT_FINDING

        return None
