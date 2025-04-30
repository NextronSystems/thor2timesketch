import os
from thor2timesketch.exceptions import JsonFileNotFoundError, JsonFileNotReadableError, JsonEmptyFileError, JsonInvalidFileExtensionError
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch import constants

logger = LoggerConfig.get_logger(__name__)


class FileValidator:
    def __init__(self) -> None:
        self.valid_extensions = constants.VALID_JSON_EXTENSIONS
        self.empty_file = constants.EMPTY_FILE

    def validate_file(self, file_path: str) -> str:
        self._check_file_exists(file_path)
        self._check_file_readable(file_path)
        self._check_file_not_empty(file_path)
        self._check_file_extension(file_path)
        logger.info(f"File '{file_path}' is valid and ready for processing.")
        return file_path


    def _check_file_exists(self, file_path: str) -> None:
        if not os.path.isfile(file_path):
            error_msg = f"File '{file_path}' does not exist."
            logger.error(error_msg)
            raise JsonFileNotFoundError(error_msg)
        logger.debug(f"File '{file_path}' is valid.")

    def _check_file_readable(self, file_path: str) -> None:
        if not os.access(file_path, os.R_OK):
            error_msg = f"File '{file_path}' is not readable."
            logger.error(error_msg)
            raise JsonFileNotReadableError(error_msg)
        logger.debug(f"File '{file_path}' is readable.")

    def _check_file_not_empty(self, file_path: str) -> None:
        if os.path.getsize(file_path) == self.empty_file:
            error_msg = f"File '{file_path}' is empty."
            logger.error(error_msg)
            raise JsonEmptyFileError(error_msg)
        logger.debug(f"File '{file_path}' is not empty.")

    def _check_file_extension(self, file_path: str) -> None:
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        if file_extension not in self.valid_extensions:
            expected = ", ".join(self.valid_extensions)
            error_msg = (
                f"Invalid file extension for '{file_path}'. "
                f"Expected one of: ['{expected}'], but got: '{file_extension}'"
            )
            logger.error(error_msg)
            raise JsonInvalidFileExtensionError(error_msg)
        logger.debug(f"File '{file_path}' has a valid extension: '{file_extension}'")