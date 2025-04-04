from typing import Dict, Any, Optional
from dateutil import parser
from datetime import timezone

from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.thor_mapper_json import THORMapperJson

logger = LoggerConfig.get_logger(__name__)

class THORMapperJsonV2(THORMapperJson):

    THOR_TIMESTAMP_FIELD = "time"
    THOR_MESSAGE_FIELD = "message"
    THOR_MODULE_FIELD = "module"

    def _get_message(self, json_line: Dict[str, Any]) -> str:
        message = json_line.get(self.THOR_MESSAGE_FIELD)
        if not message:
            logger.debug(f"No message found in THOR event, using default message.")
            message = "THOR APT scanner did not provide a message."
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
            return f"Timestamp of THOR scan execution"
        else:
            return f"{module} - {field_name}"

    def _get_additional_fields(self, json_line: Dict[str, Any], field_name: Optional[str] = None) -> Dict[str, Any]:
        exclude_fields = {self.THOR_MESSAGE_FIELD, self.THOR_TIMESTAMP_FIELD}
        return {
            field: value for field, value in json_line.items()
            if field not in exclude_fields
        }


    def _get_thor_timestamp_field(self) -> str:
        return self.THOR_TIMESTAMP_FIELD

