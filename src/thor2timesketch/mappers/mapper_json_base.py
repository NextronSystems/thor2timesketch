from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.mappers.mapped_event import MappedEvent
from thor2timesketch.utils.datetime_field import DatetimeField
from thor2timesketch.utils.timestamp_extractor import TimestampExtractor

logger = LoggerConfig.get_logger(__name__)


class MapperJsonBase(ABC):
    THOR_TIMESTAMP_FIELD: str = ""
    THOR_MESSAGE_FIELD: str = ""
    THOR_MODULE_FIELD: str = ""

    def __init__(self) -> None:
        self.timestamp_extractor: TimestampExtractor = TimestampExtractor()

    def map_thor_events(self, json_log: Dict[str, Any]) -> List[Dict[str, Any]]:

        logger.debug("Starting to map THOR events")
        events: List[Dict[str, Any]] = []

        thor_timestamp = self._get_thor_timestamp(json_log)

        thor_event = self._create_thor_scan_event(json_log)
        events.append(thor_event.to_dict())

        timestamps_from_log: List[DatetimeField] = self._get_timestamp_extract(json_log)

        ts_additional = [ts for ts in timestamps_from_log if not self.timestamp_extractor.is_same_timestamp(ts.datetime, thor_timestamp.datetime) and ts.path != thor_timestamp.path]

        if ts_additional:
            logger.debug(f"Found {len(ts_additional)} additional timestamps")
            for timestamp in ts_additional:
                event = self._create_additional_timestamp_event(json_log, timestamp)
                events.append(event.to_dict())

        logger.debug(f"Mapped {len(events)} events")
        return events

    def _create_thor_scan_event(self, json_log: Dict[str, Any]) -> MappedEvent:
        event = MappedEvent(
            message = self._get_message(json_log),
            datetime = self._get_thor_timestamp(json_log).datetime,
            timestamp_desc = self._get_timestamp_desc(json_log))
        event.add_additional(self._get_additional_fields(json_log))
        return event


    def _create_additional_timestamp_event(self, json_log: Dict[str, Any],
                                           ts_data: DatetimeField) -> MappedEvent:
        event = MappedEvent(
            message = self._get_message(json_log),
            datetime = ts_data.datetime,
            timestamp_desc = self._get_timestamp_desc(json_log, ts_data),
            time_thor_scan = self._get_thor_timestamp(json_log).datetime
        )
        event.add_additional(self._get_additional_fields(json_log))
        return event

    def _get_timestamp_extract(self, json_log: Dict[str, Any]) -> List[DatetimeField]:
        ts_extractor: List[DatetimeField] = self.timestamp_extractor.extract_datetime(json_log)
        return ts_extractor

    @abstractmethod
    def _get_message(self, json_log: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def _get_timestamp_desc(self, json_log: Dict[str, Any], ts_data: Optional[DatetimeField] = None) -> str:
        pass

    @abstractmethod
    def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        pass
    @abstractmethod
    def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> DatetimeField:
        pass

    @abstractmethod
    def check_thor_log(self, json_log: Dict[str, Any]) -> bool:
        pass
