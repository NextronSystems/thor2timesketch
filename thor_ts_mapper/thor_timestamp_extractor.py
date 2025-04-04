import re
from typing import Dict, Any, List
from thor_ts_mapper.logger_config import LoggerConfig

logger = LoggerConfig.get_logger(__name__)

class ThorTimestampExtractor:
    ISO8601_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)?$)', re.IGNORECASE) # ISO 8601 format

    @staticmethod
    def extract_datetime(thor_json_line: Dict[str, Any]) -> List[str]:
        timestamp_fields: List[str] = []

        for field, value in thor_json_line.items():
            if isinstance(value, str) and ThorTimestampExtractor.ISO8601_PATTERN.match(value):
                timestamp_fields.append(field)
        has_multiple_timestamps = len(timestamp_fields) > 1
        if has_multiple_timestamps:
            logger.debug(f"Multiple timestamp fields found: {timestamp_fields}")
        else:
            logger.debug(f"THOR timestamp field found only: {timestamp_fields}")
        return timestamp_fields