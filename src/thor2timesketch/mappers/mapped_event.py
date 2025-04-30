from typing import Dict, Any, Optional


class MappedEvent:
    def __init__(self, message: str, datetime: str, timestamp_desc: str, time_thor_scan: Optional[str] = None):
        self.message = message
        self.datetime = datetime
        self.timestamp_desc = timestamp_desc
        self.time_thor_scan = time_thor_scan
        self.additional_fields: Dict[str, Any] = {}

    def add_additional(self, additional: Dict[str, Any]) -> None:
        self.additional_fields.update(additional)

    def to_dict(self) -> Dict[str, Any]:
        event: Dict[str, Any] = {
            "message": self.message,
            "datetime": self.datetime,
            "timestamp_desc": self.timestamp_desc,
        }
        if self.time_thor_scan is not None:
            event["time_thor_scan"] = self.time_thor_scan
        event.update(self.additional_fields)
        return event