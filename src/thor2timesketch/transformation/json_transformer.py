import os
from typing import Dict, Any, Iterator
from thor2timesketch import constants
from thor2timesketch.exceptions import ProcessingError, MappingError, VersionError, InputError
from thor2timesketch.input.json_reader import JsonReader
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapper_loader import load_all_mappers

logger = LoggerConfig.get_logger(__name__)


class JsonTransformer:
    def __init__(self) -> None:
        load_all_mappers()
        self.input_reader = JsonReader()
        self.log_version_mapper = JsonLogVersion()
        self.mb_converter = constants.MB_CONVERTER

    def transform_thor_logs(self, input_json_file: str) -> Iterator[Dict[str, Any]]:
        try:
            valid_thor_logs = self.input_reader.get_valid_data(input_json_file)
            if valid_thor_logs is None:
                message_err = "No valid THOR logs found"
                logger.error(message_err)
                raise ProcessingError(message_err)

            file_size = os.path.getsize(input_json_file)
            logger.info(f"Processing input file: '{input_json_file}' ('{file_size / self.mb_converter:.2f}' MB)")
            return self._generate_mapped_logs(valid_thor_logs)
        except InputError:
            raise
        except Exception as error:
            message_err = f"Error transforming THOR logs: {error}"
            logger.error(message_err)
            raise ProcessingError(message_err) from error

    def _generate_mapped_logs(self, valid_thor_logs: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for json_line in valid_thor_logs:
            try:
                version_mapper = self.log_version_mapper.get_mapper_for_version(json_line)
                if version_mapper.check_thor_log(json_line):
                    mapped_events = version_mapper.map_thor_events(json_line)
                    for event in mapped_events:
                        yield event
            except VersionError as error:
                message_err = f"Error mapping THOR log version: {error}"
                logger.error(message_err)
                raise MappingError(message_err) from error

            except Exception as error:
                message_err = f"Error mapping THOR log: {error}"
                logger.error(message_err)
                raise MappingError(message_err) from error

        logger.debug("Finished transforming THOR logs")