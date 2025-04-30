import json
from typing import Dict, Any
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.exceptions import JsonValidationError, JsonParseError

logger = LoggerConfig.get_logger(__name__)


class JsonValidator:

    def validate_json_log(self, json_log: str) -> Dict[str, Any]:
        json_obj = self._parse_json_log(json_log)
        valid_json = self._validate_json_log(json_obj)
        return valid_json

    def _parse_json_log(self, json_log: str) -> Any:
        try:
            return json.loads(json_log)
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error: {str(e)}"
            logger.error(error_msg)
            raise JsonParseError(error_msg)

    def _validate_json_log(self, json_log: Any) -> Dict[str, Any]:
        if not isinstance(json_log, dict):
            error_msg = "Not a valid JSON object: Expected a dictionary."
            logger.error(error_msg)
            raise JsonValidationError(error_msg)
        return json_log
