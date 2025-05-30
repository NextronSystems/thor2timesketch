import yaml
from importlib.resources import files, as_file
import itertools
from typing import Dict, Any, Iterator, Optional
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.config.yaml_config_reader import YamlConfigReader
from thor2timesketch.constants import (
    DEFAULT_ENCODING,
    OUTPUT_YAML_FILE,
    DEFAULT_LEVELS,
    DEFAULT_FILTERS_YAML,
    VALID_JSON_EXTENSIONS,
    AUDIT_INFO,
    AUDIT_FINDING,
)
from thor2timesketch.exceptions import FilterConfigError, VersionError
from thor2timesketch.input.json_reader import JsonReader
from thor2timesketch.input.file_validator import FileValidator
from thor2timesketch.mappers.json_log_version import JsonLogVersion
from thor2timesketch.mappers.mapper_json_v1 import MapperJsonV1
from thor2timesketch.mappers.mapper_json_v2 import MapperJsonV2
from pathlib import Path


class FilterCreator:
    def __init__(self, input_file: Optional[Path] = None) -> None:
        self.input_file = input_file
        self.json_reader = JsonReader()
        self.mapper_resolver = JsonLogVersion()

    def generate_yaml_file(self) -> None:
        try:
            if self.input_file:
                validator = FileValidator(valid_extensions=VALID_JSON_EXTENSIONS)
                valid_input_file = validator.validate_file(self.input_file)
                events = self.json_reader.get_valid_data(valid_input_file)
                first_event = next(events)
                mapper = self.mapper_resolver.get_mapper_for_version(first_event)
                if isinstance(mapper, (MapperJsonV1, MapperJsonV2)):
                    config = self._build_filters_from_json_thor(first_event, events)
                else:
                    ConsoleConfig.warning(
                        f"This {self.input_file} isn’t supported filters extraction, generating default filter configuration."
                    )
                    config = self._load_default_config()
            else:
                config = self._load_default_config()

            self._write_config(config)
        except VersionError:
            ConsoleConfig.warning(
                "Use -h or --help for finding more information to generate default filter configuration."
            )
            raise FilterConfigError(
                f"'{self.input_file}' does not contains filters to be extracted."
            )
        except Exception as e:
            raise FilterConfigError(
                f"Failed to generate filter configuration: {e}"
            ) from e

    def _build_filters_from_json_thor(
        self, first: Dict[str, Any], json_logs: Iterator[Dict[str, Any]]
    ) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            "filters": {
                "levels": list(DEFAULT_LEVELS),
                "modules": {"include": [], "exclude": []},
                "features": {"include": [], "exclude": []},
                "audit": [AUDIT_INFO, AUDIT_FINDING],
            }
        }
        for entry in itertools.chain([first], json_logs):
            message = entry.get("message", "")
            if message.startswith("Selected modules:"):
                config["filters"]["modules"]["include"].extend(
                    self._parse_filters("Selected modules:", message)
                )
            elif message.startswith("Deselected modules:"):
                config["filters"]["modules"]["exclude"].extend(
                    self._parse_filters("Deselected modules:", message)
                )
            elif message.startswith("Selected features:"):
                config["filters"]["features"]["include"].extend(
                    self._parse_filters("Selected features:", message)
                )
            elif message.startswith("Deselected features:"):
                config["filters"]["features"]["exclude"].extend(
                    self._parse_filters("Deselected features:", message)
                )
        return config

    def _load_default_config(self) -> Dict[str, Any]:
        ConsoleConfig.info("Default filter configuration will be generated.")
        try:
            default_filter_path = files("thor2timesketch.config").joinpath(
                DEFAULT_FILTERS_YAML
            )
            with as_file(default_filter_path) as filter_file:
                return YamlConfigReader.load_yaml(filter_file)
        except FilterConfigError as e:
            raise FilterConfigError(
                f"Failed to load default filter '{filter_file}': {e}"
            )

    def _write_config(self, config: Dict[str, Any]) -> None:
        output_file = Path.cwd() / OUTPUT_YAML_FILE
        ConsoleConfig.info(f"Creating filter configuration at `{output_file}`")
        try:
            with output_file.open("w", encoding=DEFAULT_ENCODING) as file:
                yaml.safe_dump(config, file, sort_keys=False)
        except Exception as e:
            error_msg = f"Failed to write filter configuration to '{output_file}': {e}"
            ConsoleConfig.error(error_msg)
            raise FilterConfigError(error_msg) from e
        ConsoleConfig.success(
            f"Filter configuration successfully written to '{output_file}'"
        )

    def _parse_filters(self, prefix: str, message: str) -> list[str]:
        modules_features = message[len(prefix) :].strip()
        return [item.strip() for item in modules_features.split(",") if item.strip()]
