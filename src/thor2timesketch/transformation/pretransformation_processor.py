from typing import Dict, Any, Iterator, Optional
from thor2timesketch.constants import LOG_VERSION, AUDIT_FINDING, AUDIT_INFO
from thor2timesketch.utils.audit_events_extractor import AuditEventsExtractor
from thor2timesketch.config.filter_audit import FilterAudit
from pathlib import Path


class PreTransformationProcessor:
    def __init__(self, filter_path: Optional[Path] = None) -> None:
        self._audit_filter = FilterAudit.read_audit_yaml(filter_path)

    def transformation(self, valid_json: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        if LOG_VERSION in valid_json:
            yield valid_json
            return
        selector = self._audit_filter.get_audit_trail_selector(valid_json)

        if selector == AUDIT_FINDING:
            yield from AuditEventsExtractor.extract_findings(valid_json)
            return
        elif selector == AUDIT_INFO:
            info = AuditEventsExtractor.extract_info(valid_json)
            if info:
                yield info
                return
