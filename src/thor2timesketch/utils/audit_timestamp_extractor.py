from typing import Dict, Any, List

from thor2timesketch.constants import AUDIT_TIMESTAMP
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.utils.timestamp_extractor import TimestampExtractor


class AuditTimestampExtractor(TimestampExtractor):

    def extract(self, data: Dict[str, Any]) -> List[DatetimeField]:
        timestamps = data.pop(AUDIT_TIMESTAMP, {})
        return [
            DatetimeField(path=key, datetime=value) for key, value in timestamps.items()
        ]
