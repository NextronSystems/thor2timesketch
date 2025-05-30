from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.exceptions import (
    MappingError,
    TimestampError,
    FlattenJsonError,
    ProcessingError,
)
from thor2timesketch.mappers.mapped_event import MappedEvent
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.utils.normalizer import JsonNormalizer, IdentityNormalizer
from thor2timesketch.utils.regex_timestamp_extractor import RegexTimestampExtractor
from thor2timesketch.utils.timestamp_extractor import TimestampExtractor
from thor2timesketch.utils.thor_finding_id import ThorFindingId


class MapperJsonBase(ABC):
    THOR_TIMESTAMP_FIELD: str = ""
    THOR_MESSAGE_FIELD: str = ""
    THOR_MODULE_FIELD: str = ""
    THOR_LEVEL_FIELD: str = ""

    def __init__(
        self,
        normalizer: Optional[JsonNormalizer] = None,
        time_extractor: Optional[TimestampExtractor] = None,
    ) -> None:
        self.timestamp_extractor: TimestampExtractor = (
            time_extractor if time_extractor is not None else RegexTimestampExtractor()
        )
        self.normalizer: JsonNormalizer = (
            normalizer if normalizer is not None else IdentityNormalizer()
        )

    def map_thor_events(self, json_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            ConsoleConfig.debug("Starting to map THOR events")
            normalized_json = self.normalizer.normalize(json_log)
            events: List[Dict[str, Any]] = []

            event_group_id = ThorFindingId.get_finding_id()

            thor_timestamp = self._get_thor_timestamp(normalized_json)
            thor_event = self._create_thor_event(normalized_json, event_group_id)
            events.append(thor_event.to_dict())

            all_timestamps: List[DatetimeField] = self._get_timestamp_extract(
                normalized_json
            )
            additional_timestamp = [
                time
                for time in all_timestamps
                if not self.timestamp_extractor.is_same_timestamp(
                    time.datetime, thor_timestamp.datetime
                )
                and time.path != thor_timestamp.path
            ]

            if additional_timestamp:
                ConsoleConfig.debug(
                    f"Found {len(additional_timestamp)} additional timestamps"
                )
                for timestamp in additional_timestamp:
                    event = self._create_additional_timestamp_event(
                        normalized_json, timestamp, event_group_id
                    )
                    events.append(event.to_dict())

            ConsoleConfig.debug(f"Mapped {len(events)} events")
            return events
        except (MappingError, TimestampError, FlattenJsonError) as e:
            raise ProcessingError(f"Error while mapping events: {e}") from e
        except Exception as e:
            raise ProcessingError(f"Unexpected error while mapping events: {e}") from e

    def _create_thor_event(
        self, json_log: Dict[str, Any], event_group_id: str
    ) -> MappedEvent:
        event = MappedEvent(
            message=self._get_message(json_log),
            datetime=self._get_thor_timestamp(json_log).datetime,
            timestamp_desc=self._get_timestamp_desc(
                json_log, self._get_thor_timestamp(json_log)
            ),
            event_group_id=event_group_id,
            tag=self._get_thor_tags(json_log),
        )

        event.add_additional(self._get_additional_fields(json_log))
        return event

    def _create_additional_timestamp_event(
        self, json_log: Dict[str, Any], time_data: DatetimeField, event_group_id: str
    ) -> MappedEvent:
        event = MappedEvent(
            message=self._get_message(json_log),
            datetime=time_data.datetime,
            timestamp_desc=self._get_timestamp_desc(json_log, time_data),
            event_group_id=event_group_id,
            tag=self._get_additional_tags(json_log),
        )
        return event

    def _get_timestamp_extract(self, json_log: Dict[str, Any]) -> List[DatetimeField]:
        time_extractor: List[DatetimeField] = self.timestamp_extractor.extract(json_log)
        return time_extractor

    def requires_filter(self) -> bool:
        return True

    @abstractmethod
    def _get_message(self, json_log: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def _get_timestamp_desc(
        self, json_log: Dict[str, Any], time_data: DatetimeField
    ) -> str:
        pass

    @abstractmethod
    def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> DatetimeField:
        pass

    @abstractmethod
    def get_filterable_fields(
        self, json_log: Dict[str, Any]
    ) -> tuple[Optional[str], Optional[str]]:
        pass

    @abstractmethod
    def _get_thor_tags(self, json_log: Dict[str, Any]) -> List[str]:
        pass

    @abstractmethod
    def _get_additional_tags(self, json_log: Dict[str, Any]) -> List[str]:
        pass
