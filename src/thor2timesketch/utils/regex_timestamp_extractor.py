import re
from collections import deque
from datetime import timezone
from typing import Dict, Any, List, Tuple
from dateutil import parser
from thor2timesketch.constants import ISO8601_PATTERN
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.exceptions import TimestampError
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.utils.timestamp_extractor import TimestampExtractor


class RegexTimestampExtractor(TimestampExtractor):

    def __init__(self) -> None:
        self.ISO8601 = re.compile(ISO8601_PATTERN, re.IGNORECASE)

    def extract(self, data_json: Dict[str, Any]) -> List[DatetimeField]:

        if data_json is None:
            raise TimestampError(
                "Received an empty THOR log as input for timestamp extractor."
            )

        timestamps: List[DatetimeField] = []
        queue: deque[Tuple[Dict[str, Any], str]] = deque([(data_json, "")])

        try:
            while queue:
                log_json, path = queue.popleft()

                if isinstance(log_json, dict):
                    for log_field, log_value in log_json.items():
                        new_path = f"{path} {log_field}" if path else log_field
                        queue.append((log_value, new_path))
                elif isinstance(log_json, list):
                    for log_value in log_json:
                        queue.append((log_value, path))
                else:
                    if isinstance(log_json, str) and self.ISO8601.match(log_json):
                        try:
                            parsed_date = parser.isoparse(log_json)
                            if parsed_date.tzinfo is None:
                                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                            iso_data = parsed_date.isoformat()
                            ConsoleConfig.debug(
                                f"Found ISO8601 date {iso_data} at path {path}"
                            )
                            timestamps.append(
                                DatetimeField(path=path, datetime=iso_data)
                            )
                        except (ValueError, TypeError) as e:
                            raise TimestampError(
                                f"Error parsing date '{log_json}' at path '{path}': {e}"
                            )

        except Exception as e:
            raise TimestampError(f"Unexpected error during timestamp extraction: {e}")
        return timestamps
