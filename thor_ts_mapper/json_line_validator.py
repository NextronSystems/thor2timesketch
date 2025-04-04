import json
from typing import Dict, Any, Tuple, Optional
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.exceptions import JsonValidationError

logger = LoggerConfig.get_logger(__name__)


class JSONLineValidator:

    @staticmethod
    def validate_json(json_str: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        try:
            json_obj = json.loads(json_str)
            return JSONLineValidator._validate_json_object(json_obj)
        except json.JSONDecodeError as e:
            raise JsonValidationError(f"JSON decode error: {str(e)}")

    @staticmethod
    def _validate_json_object(json_obj: Any) -> Tuple[bool, Optional[Dict[str, Any]]]:
        if not isinstance(json_obj, dict):
            logger.error("Not a valid JSON object")
            return False, None

        logger.debug("JSON validation successful")
        return True, json_obj
