import json
from typing import Dict, Any, Tuple, Optional
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.exceptions import JsonValidationError

logger = LoggerConfig.get_logger(__name__)


class JSONLineValidator:

    @staticmethod
    def validate_json(json_str: str) -> Dict[str, Any]:
        try:
            json_obj = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise JsonValidationError(f"JSON decode error: {str(e)}")

        return JSONLineValidator._validate_json_object(json_obj)

    @staticmethod
    def _validate_json_object(json_obj: Any) -> Dict[str, Any]:
        if not isinstance(json_obj, dict):
            logger.error("Not a valid JSON object")
            raise JsonValidationError("Not a valid JSON object: Expected a dictionary.")

        logger.debug("JSON validation successful")
        return  json_obj
