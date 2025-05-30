from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapper_json_v1 import MapperJsonV1


@JsonLogVersion.log_version("v2.0.0")
class MapperJsonV2(MapperJsonV1):
    def __init__(self) -> None:
        super().__init__()
