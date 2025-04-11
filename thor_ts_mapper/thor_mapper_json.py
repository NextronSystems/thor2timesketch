from abc import abstractmethod, ABC
from typing import Dict, Any, List, Optional
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.thor_timestamp_extractor import ThorTimestampExtractor
from dateutil import parser
from datetime import timezone
logger = LoggerConfig.get_logger(__name__)

class THORMapperJson:
    THOR_TIMESTAMP_FIELD: str = ""
    THOR_MESSAGE_FIELD: str = ""
    THOR_MODULE_FIELD: str = ""

    def map_thor_events(self, json_line: Dict[str, Any]) -> List[Dict[str, Any]]:

        timestamps_fields = THORMapperJson._get_timestamp_extract(json_line)
        thor_timestamp = self._get_thor_timestamp_field()
        additional_timestamp_fields = [field for field in timestamps_fields if field != thor_timestamp]

        events: List[Dict[str, Any]] = []

        thor_event_map = self._create_thor_scan_event(json_line)
        events.append(thor_event_map)
        if additional_timestamp_fields:
            for field_name in additional_timestamp_fields:
                event = self._create_additional_timestamp_event(json_line, field_name)
                events.append(event)

        logger.debug(f"Mapped {len(events)} events")
        return events


    def _create_thor_scan_event(self, json_line: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            'message': self._get_message(json_line),
            'datetime': self._get_datetime(json_line),
            'timestamp_desc': self._get_timestamp_desc(json_line),
        }
        event.update(self._get_additional_fields(json_line))
        return event

    def _create_additional_timestamp_event(self, json_line: Dict[str, Any],
                                          field_name: str) -> Dict[str, Any]:
        event = {
            'message': self._get_message(json_line),
            'datetime': self._get_datetime(json_line, field_name),
            'timestamp_desc': self._get_timestamp_desc(json_line, field_name),
            'time_thor_scan': self._get_datetime(json_line)
        }
        event.update(self._get_additional_fields(json_line, field_name))
        return event

    @staticmethod
    def _get_timestamp_extract(json_line: Dict[str, Any]) -> List[str]:
        return ThorTimestampExtractor.extract_datetime(json_line)


    def _get_message(self, json_line: Dict[str, Any]) -> str:
        message = json_line.get(self.THOR_MESSAGE_FIELD)
        if not message:
            logger.debug("No message found in THOR event, using default message.")
            message = "THOR APT scanner message."
        return message

    def _get_datetime(self, json_line: Dict[str, Any], field_name: Optional[str] = None) -> str:
        field = field_name if field_name is not None else self._get_thor_timestamp_field()
        value = json_line.get(field)
        try:
            timestamp = parser.isoparse(value)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            return timestamp.isoformat()
        except (ValueError, TypeError):
            logger.error(f"Invalid datetime format at {field}: {value}")
            return value


    def _get_timestamp_desc(self, json_line: Dict[str, Any], field_name: Optional[str] = None) -> str:
        module = json_line.get(self.THOR_MODULE_FIELD)
        if field_name is None or field_name == self._get_thor_timestamp_field():
            return "Timestamp of THOR scan execution"
        else:
            return f"{module} - {field_name}"

    def _get_additional_fields(self, json_line: Dict[str, Any], field_name: Optional[str] = None) -> Dict[str, Any]:
        exclude_fields = {self.THOR_MESSAGE_FIELD, self._get_thor_timestamp_field()}
        return {
            field: value for field, value in json_line.items()
            if field not in exclude_fields
        }

    def _get_thor_timestamp_field(self) -> str:
        return self.THOR_TIMESTAMP_FIELD



