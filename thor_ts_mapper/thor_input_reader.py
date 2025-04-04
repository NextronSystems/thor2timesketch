from typing import Iterator, Dict, Tuple, Optional
from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.exceptions import FileValidationError, JsonValidationError
from thor_ts_mapper.file_validator import FileValidator
from thor_ts_mapper.json_line_validator import JSONLineValidator

logger = LoggerConfig.get_logger(__name__)

class THORJSONInputReader:
    @staticmethod
    def _validate_file(input_file: str) -> bool:
        try:
            FileValidator.validate_file(input_file)
            return True
        except FileValidationError as e:
            logger.error("File validation error: %s", e)
            return False

    @staticmethod
    def get_valid_json(input_file: str) -> Tuple[bool, Optional[Iterator[Dict]]]:
        if not THORJSONInputReader._validate_file(input_file):
            return False, None

        def json_generator() -> Iterator[Dict]:
            try:
                with open(input_file, 'r', encoding='utf-8') as file:
                    for line_num, line in enumerate(file, 1):
                        try:
                            is_valid, json_data = JSONLineValidator.validate_json(line)
                            if is_valid and json_data is not None:
                                yield json_data
                        except JsonValidationError as e:
                            logger.error(f"Invalid JSON at line {line_num}: {e}")
            except IOError as e:
                logger.error(f"Error opening or reading file: {e}")
                return

        return True, json_generator()

