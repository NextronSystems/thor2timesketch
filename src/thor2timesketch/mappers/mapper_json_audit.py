from typing import Dict, Any, List
from abc import abstractmethod
from thor2timesketch.exceptions import (
    MappingError,
    ProcessingError,
    TimestampError,
    FlattenJsonError,
)
from thor2timesketch.mappers.mapped_event import MappedEvent
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from thor2timesketch.utils.audit_timestamp_extractor import AuditTimestampExtractor
from thor2timesketch.utils.normalizer import AuditTrailNormalizer
from thor2timesketch.utils.thor_finding_id import ThorFindingId
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.config.console_config import ConsoleConfig


class MapperJsonAudit(MapperJsonBase):

    def __init__(self) -> None:
        super().__init__(
            normalizer=AuditTrailNormalizer(), time_extractor=AuditTimestampExtractor()
        )

    def map_thor_events(self, json_log: Dict[str, Any]) -> list[dict[str, Any]]:
        try:
            ConsoleConfig.debug("Starting to map THOR audit events")
            events: List[Dict[str, Any]] = []
            all_timestamps = self.timestamp_extractor.extract(json_log)
            normalized = self.normalizer.normalize(json_log)
            event_group_id = ThorFindingId.get_finding_id()
            for index, time_data in enumerate(all_timestamps):
                primary = index == 0
                event = self._create_audit_event(
                    normalized, time_data, event_group_id, primary
                )
                events.append(event.to_dict())
            ConsoleConfig.debug(f"Mapped '{len(events)}' THOR audit events")
            return events
        except (MappingError, TimestampError, FlattenJsonError) as e:
            raise ProcessingError(f"Error while mapping audit events: {e}") from e
        except Exception as e:
            raise ProcessingError(f"Unexpected error while mapping audit events: {e}")

    @abstractmethod
    def _create_audit_event(
        self,
        json_log: Dict[str, Any],
        time_data: DatetimeField,
        event_group_id: str,
        primary: bool,
    ) -> MappedEvent:
        pass
