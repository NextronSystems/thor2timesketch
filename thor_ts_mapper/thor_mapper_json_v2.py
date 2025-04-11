from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.thor_mapper_json import THORMapperJson

logger = LoggerConfig.get_logger(__name__)

class THORMapperJsonV2(THORMapperJson):

    THOR_TIMESTAMP_FIELD = "time"
    THOR_MESSAGE_FIELD = "message"
    THOR_MODULE_FIELD = "module"
