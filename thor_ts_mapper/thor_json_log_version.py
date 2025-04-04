from typing import Dict, Any
from thor_ts_mapper.thor_mapper_json import THORMapperJson
from thor_ts_mapper.thor_mapper_json_v2 import THORMapperJsonV2
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.thor_mapper_json_v3 import THORMapperJsonV3

logger = LoggerConfig.get_logger(__name__)

class THORJSONLogVersionMapper:
    @staticmethod
    def get_mapper(json_line: Dict[str, Any]) -> THORMapperJson:
        log_version = json_line.get("log_version").lower()
        if log_version.startswith("v1"):
            logger.debug("Detected log version v2; using THORMapperJsonV2")
            return THORMapperJsonV2()
        elif log_version.startswith("v3"):
            logger.debug("Detected log version v3; using THORMapperJsonV3")
            return THORMapperJsonV3()
        else:
            logger.error(f"Log version {log_version} is not supported", log_version)
            raise ValueError(f"Unsupported log version: {log_version}")