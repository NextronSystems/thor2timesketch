from typing import Any, Dict, Iterator, Optional
from thor2timesketch.constants import AUDIT_TIMESTAMP, AUDIT_FINDING, AUDIT_INFO


class AuditEventsExtractor:

    @staticmethod
    def extract_findings(audit_json: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        findings = audit_json.get(AUDIT_FINDING) or []
        for finding in findings:
            timestamps = finding.get(AUDIT_TIMESTAMP)
            if isinstance(timestamps, dict) and bool(timestamps):
                yield finding

    @staticmethod
    def extract_info(audit_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        info = audit_json.get(AUDIT_INFO)
        if not isinstance(info, dict) or not info:
            return None
        timestamps = info.get(AUDIT_TIMESTAMP)
        if not isinstance(timestamps, dict) or not timestamps:
            return None
        return info
