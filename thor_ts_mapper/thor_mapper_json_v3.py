from typing import Dict, Any, Optional
from thor_ts_mapper.thor_mapper_json import THORMapperJson


class THORMapperJsonV3(THORMapperJson):
    THOR_TIMESTAMP_FIELD = "meta_time"
    THOR_MESSAGE_FIELD = "summary"
    THOR_MODULE_FIELD = "meta_module"