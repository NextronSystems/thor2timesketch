from typing import List, Dict, Any, Optional
from thor2timesketch.exceptions import MappingError, TimestampError
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.constants import THOR_TAG, EXTRA_TAG
from thor2timesketch.utils.normalizer import FlatteningNormalizer
from thor2timesketch.utils.regex_timestamp_extractor import RegexTimestampExtractor


@JsonLogVersion.log_version("v1.0.0")
class MapperJsonV1(MapperJsonBase):

    THOR_TIMESTAMP_FIELD: str = "time"
    THOR_MESSAGE_FIELD: str = "message"
    THOR_MODULE_FIELD: str = "module"
    THOR_LEVEL_FIELD: str = "level"

    def __init__(self) -> None:
        self.normalizer = FlatteningNormalizer()
        self.timestamp_extractor = RegexTimestampExtractor()
        super().__init__(self.normalizer, self.timestamp_extractor)

    def _get_message(self, json_log: Dict[str, Any]) -> str:
        message = json_log.get(self.__class__.THOR_MESSAGE_FIELD)
        if not isinstance(message, str):
            raise MappingError(f"Missing required {message} field in JSON log")
        return message

    def _get_timestamp_desc(
        self, json_log: Dict[str, Any], time_data: DatetimeField
    ) -> str:
        if time_data is None or time_data.path == self.__class__.THOR_TIMESTAMP_FIELD:
            return "THOR scan timestamp"
        module = json_log.get(self.__class__.THOR_MODULE_FIELD)
        if not isinstance(module, str):
            raise MappingError(
                f"Missing required {module} field for timestamp description"
            )
        return f"{module} - {time_data.path}"

    def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        exclude_thor_timestamp = self.__class__.THOR_TIMESTAMP_FIELD
        additional_fields = {
            key: value
            for key, value in json_log.items()
            if key not in [exclude_thor_timestamp]
        }
        return additional_fields

    def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> DatetimeField:
        thor_timestamp = json_log.get(self.__class__.THOR_TIMESTAMP_FIELD)
        if not isinstance(thor_timestamp, str):
            raise TimestampError(
                f"Missing required '{self.__class__.THOR_TIMESTAMP_FIELD}' field in JSON log"
            )
        return DatetimeField(
            path=self.__class__.THOR_TIMESTAMP_FIELD, datetime=thor_timestamp
        )

    def _get_thor_tags(self, json_log: Dict[str, Any]) -> List[str]:
        type_event = json_log.get(self.__class__.THOR_LEVEL_FIELD)
        if not isinstance(type_event, str):
            raise MappingError(f"Missing required {type_event} field for tags")
        return [THOR_TAG, type_event]

    def _get_additional_tags(self, json_log: Dict[str, Any]) -> List[str]:
        type_event = json_log.get(self.__class__.THOR_LEVEL_FIELD)
        if not isinstance(type_event, str):
            raise MappingError(
                f"Missing required {type_event} field for additional tags"
            )
        return [EXTRA_TAG, type_event]

    def get_filterable_fields(
        self, json_log: Dict[str, Any]
    ) -> tuple[Optional[str], Optional[str]]:
        level = json_log.get(self.__class__.THOR_LEVEL_FIELD)
        module = json_log.get(self.__class__.THOR_MODULE_FIELD)
        return level, module
