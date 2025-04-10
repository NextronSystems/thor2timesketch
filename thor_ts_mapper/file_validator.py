import os
from thor_ts_mapper.exceptions import JsonFileNotFoundError, JsonFileNotReadableError, JsonEmptyFileError, JsonInvalidFileExtensionError
from thor_ts_mapper.logger_config import LoggerConfig

logger = LoggerConfig.get_logger(__name__)


class FileValidator:

    VALID_EXTENSIONS = (".json", ".jsonl")

    @staticmethod
    def validate_file(thor_json_file: str) -> str:

        FileValidator._check_file_exists(thor_json_file)
        FileValidator._check_file_readable(thor_json_file)
        FileValidator._check_file_not_empty(thor_json_file)
        FileValidator._check_file_extension(thor_json_file)

        logger.info(f"File validation successful: {thor_json_file}")
        return thor_json_file

    @staticmethod
    def _check_file_exists(thor_json_file: str) -> None:
        if not os.path.isfile(thor_json_file):
            logger.error(f"File {thor_json_file} does not exist.")
            raise JsonFileNotFoundError(f"File {thor_json_file} does not exist")

    @staticmethod
    def _check_file_readable(thor_json_file: str) -> None:
        if not os.access(thor_json_file, os.R_OK):
            logger.error(f"File {thor_json_file} is not readable.")
            raise JsonFileNotReadableError(f"File {thor_json_file} is not readable")

    @staticmethod
    def _check_file_not_empty(thor_json_file: str) -> None:
        if os.path.getsize(thor_json_file) == 0:
            logger.error(f"File {thor_json_file} is empty.")
            raise JsonEmptyFileError(f"File {thor_json_file} is empty")

    @staticmethod
    def _check_file_extension(file_path: str) -> None:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in FileValidator.VALID_EXTENSIONS:
            logger.error(
                f"File {file_path} does not have a .json or .jsonl extension"
            )
            raise JsonInvalidFileExtensionError(
                f"File {file_path} does not have a .json or .jsonl extension"
            )