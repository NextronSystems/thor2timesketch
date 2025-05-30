from typing import Dict, Any, List, Optional
from thor2timesketch.exceptions import MappingError
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapped_event import MappedEvent
from thor2timesketch.mappers.mapper_json_audit import MapperJsonAudit
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.constants import AUDIT_INFO_TAG


@JsonLogVersion.log_version("info")
class MapperJsonAuditInfo(MapperJsonAudit):
    THOR_NAME_FIELD = "Name"

    def _create_audit_event(
        self,
        json_log: Dict[str, Any],
        time_data: DatetimeField,
        event_group_id: str,
        primary: bool,
    ) -> MappedEvent:
        event = MappedEvent(
            message=self._get_message(json_log),
            datetime=time_data.datetime,
            timestamp_desc=self._get_timestamp_desc(json_log, time_data),
            event_group_id=event_group_id,
            tag=self._get_additional_tags(json_log),
        )
        if primary:
            event.add_additional(self._get_additional_fields(json_log))

        return event

    def _get_message(self, json_log: Dict[str, Any]) -> str:
        message = json_log.get(self.__class__.THOR_NAME_FIELD)
        if not isinstance(message, str):
            raise MappingError(f"Invalid or missing 'Name' field: {message}")
        return message

    def _get_timestamp_desc(
        self, json_log: Dict[str, Any], time_data: DatetimeField
    ) -> str:
        return f"{time_data.path}"

    def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in json_log.items()}

    def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> DatetimeField:
        raise MappingError("Audit info logs do not have a scan timestamp field")

    def get_filterable_fields(
        self, json_log: Dict[str, Any]
    ) -> tuple[Optional[str], Optional[str]]:
        return None, None

    def _get_thor_tags(self, json_log: Dict[str, Any]) -> List[str]:
        raise MappingError("Audit info logs do not have a scan tag field")

    def _get_additional_tags(self, json_log: Dict[str, Any]) -> List[str]:
        return [AUDIT_INFO_TAG]

    def requires_filter(self) -> bool:
        return False
