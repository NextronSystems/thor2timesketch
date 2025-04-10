from typing import Iterator, Dict, Generator
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.exceptions import FileValidationError, JsonValidationError
from thor_ts_mapper.file_validator import FileValidator
from thor_ts_mapper.json_line_validator import JSONLineValidator

logger = LoggerConfig.get_logger(__name__)

class THORJSONInputReader:
    @staticmethod
    def _validate_file(input_file: str) -> str:
        try:
            valid_file = FileValidator.validate_file(input_file)
        except FileValidationError as e:
            logger.error("File validation error: %s", e)
            raise
        return valid_file

    @staticmethod
    def get_valid_json(input_file: str) -> Iterator[Dict]:

        valid_file = THORJSONInputReader._validate_file(input_file)

        def generate_valid_json() -> Generator[Dict, None, None]:
            try:
                with open(valid_file, 'r', encoding='utf-8') as file:
                    for line_num, line in enumerate(file, 1):
                        try:
                            json_data = JSONLineValidator.validate_json(line)
                            if json_data is not None:
                                yield json_data
                        except JsonValidationError as e:
                            logger.error(f"Invalid JSON at line {line_num}: {e}")
            except IOError as e:
                logger.error(f"Error opening or reading file: {e}")
                raise

        return generate_valid_json()