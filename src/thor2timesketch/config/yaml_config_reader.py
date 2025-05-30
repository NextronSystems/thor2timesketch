from thor2timesketch.constants import (
    VALID_YAML_EXTENSIONS,
    DEFAULT_ENCODING,
    YAML_FILTERS,
)
from thor2timesketch.exceptions import FilterConfigError, FileValidationError
from thor2timesketch.input.file_validator import FileValidator
from typing import Dict, Any
import yaml
from pathlib import Path


class YamlConfigReader:

    @staticmethod
    def load_yaml(config_path: Path) -> Dict[str, Any]:
        try:
            validator = FileValidator(valid_extensions=VALID_YAML_EXTENSIONS)
            yaml_file = validator.validate_file(config_path)
        except FileValidationError as e:
            raise FilterConfigError(f"Invalid YAML file `{config_path}`: {e}") from e
        try:
            with yaml_file.open("r", encoding=DEFAULT_ENCODING) as file:
                content = yaml.safe_load(file) or {}
        except yaml.YAMLError as e:
            raise FilterConfigError(f"YAML parse error in {yaml_file}: {e}") from e
        except UnicodeDecodeError as e:
            raise FilterConfigError(f"Encoding error in {yaml_file}: {e}") from e
        except Exception as e:
            raise FilterConfigError(f"Unexpected error in {yaml_file}: {e}") from e
        filters = content.get(YAML_FILTERS)
        if not isinstance(filters, dict):
            raise FilterConfigError(f"Invalid filter config format in {yaml_file}")
        return content
