from typing import Iterator, Dict, Any, Union
from thor2timesketch.exceptions import (
    JsonValidationError,
    InputError,
    JsonParseError,
    FileValidationError,
)
from thor2timesketch.input.file_validator import FileValidator
from thor2timesketch.input.json_validator import JsonValidator
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.constants import VALID_JSON_EXTENSIONS, DEFAULT_ENCODING
from pathlib import Path


class JsonReader:

    def __init__(self) -> None:
        self.file_validator = FileValidator(valid_extensions=VALID_JSON_EXTENSIONS)
        self.json_validator = JsonValidator()

    def _validate_file(self, input_file: Union[str, Path]) -> Path:
        valid_file: Path = self.file_validator.validate_file(input_file)
        return valid_file

    def get_valid_data(self, input_file: Union[str, Path]) -> Iterator[Dict[str, Any]]:
        try:
            valid_file = self._validate_file(input_file)
            ConsoleConfig.info("File is valid and ready for processing.")
        except FileValidationError as e:
            raise InputError(f"File validation error: {e}") from e
        return self._generate_valid_json(valid_file)

    def _generate_valid_json(self, valid_file: Path) -> Iterator[Dict[str, Any]]:
        try:
            with valid_file.open("r", encoding=DEFAULT_ENCODING) as file:
                for line_num, line in enumerate(file, start=1):
                    try:
                        json_data = self.json_validator.validate_json_log(line)
                        if json_data is not None:
                            yield json_data
                    except (JsonParseError, JsonValidationError) as error:
                        raise InputError(
                            f"Error parsing JSON at line {line_num}: {error}"
                        )
        except IOError as error:
            raise InputError(
                f"Error opening or reading file '{valid_file}': {error}"
            ) from error
