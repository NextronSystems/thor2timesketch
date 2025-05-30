import json
from typing import Dict, Any, Optional
from thor2timesketch.exceptions import JsonValidationError, JsonParseError


class JsonValidator:

    def validate_json_log(self, json_log: str) -> Optional[Dict[str, Any]]:
        if not json_log.strip():
            return None
        json_obj = self._parse_json_log(json_log)
        valid_json = self._validate_json_log(json_obj)
        return valid_json

    def _parse_json_log(self, json_log: str) -> Dict[str, Any]:
        try:
            result: Dict[str, Any] = json.loads(json_log)
        except json.JSONDecodeError as e:
            raise JsonParseError(f"JSON decode error: {e}")
        return result

    def _validate_json_log(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(json_log, dict):
            raise JsonValidationError("Not a valid JSON object: expected a dictionary.")
        return json_log
