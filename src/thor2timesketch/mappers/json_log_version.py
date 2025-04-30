from typing import Dict, Any, Type, Callable
from thor2timesketch.exceptions import VersionError
from thor2timesketch.mappers.mapper_json_base import MapperJsonBase
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch import constants

logger = LoggerConfig.get_logger(__name__)

class JsonLogVersion:

    _mapper_log_version: Dict[str, Type["MapperJsonBase"]] = {}

    @classmethod
    def log_version(cls, log_version: str) -> Callable[[Type["MapperJsonBase"]], Type["MapperJsonBase"]]:
        def map_log_version(mapper_cls: Type["MapperJsonBase"]) -> Type["MapperJsonBase"]:
            cls._mapper_log_version[log_version.lower()] = mapper_cls
            logger.debug(f"Mapping log version {log_version} to {mapper_cls}")
            return mapper_cls
        return map_log_version

    def get_mapper_for_version(self, json_line: Dict[str, Any]) -> "MapperJsonBase":
        thor_version = json_line.get(constants.LOG_VERSION)
        if not isinstance(thor_version, str):
            raise VersionError(f"Invalid or missing log_version: {thor_version}")

        thor_mapper = next((mapper for version, mapper in self._mapper_log_version.items() if thor_version == version), None)
        if thor_mapper is None:
            raise VersionError(f'The mapper for version "{thor_version}" is not implemented')
        return thor_mapper()
