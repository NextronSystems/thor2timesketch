# from typing import Dict, Any, Optional
#
# from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
# from thor2timesketch.mappers.json_log_version import JsonLogVersion
# from thor2timesketch.utils.datetime_field import DatetimeField
#
#
# @JsonLogVersion.log_version("v3.0.0")
# class MapperJsonV3(MapperJsonBase):
#
#     THOR_TIMESTAMP_FIELD: str = "meta time"
#     THOR_MESSAGE_FIELD: str = "summary"
#     THOR_MODULE_FIELD: str = "meta module"
#
#     def _get_message(self, json_log: Dict[str, Any]) -> str:
#         pass
#
#     def _get_timestamp_desc(self, json_log: Dict[str, Any], ts_data: Optional[DatetimeField] = None) -> str:
#         pass
#
#     def _get_additional_fields(self, json_log: Dict[str, Any]) -> Dict[str, Any]:
#         pass
#
#     def _get_thor_timestamp(self, json_log: Dict[str, Any]) -> str:
#         pass