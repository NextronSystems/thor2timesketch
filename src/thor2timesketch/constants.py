VALID_JSON_EXTENSIONS = [".json", ".jsonl"]
VALID_YAML_EXTENSIONS = [".yaml", ".yml"]
DEFAULT_ENCODING = "utf-8"
EMPTY_FILE = 0
MB_CONVERTER = 1024 * 1024
ISO8601_PATTERN = (
    r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)?$)"
)
LOG_VERSION = "log_version"
OUTPUT_FILE_EXTENSION = ".jsonl"
TS_SCOPE = ["user", "shared"]
MAX_WRITE_ERRORS = 5
PREFIX = "TF"
THOR_TAG = "thor"
EXTRA_TAG = "ts_extra"
DELIMITER = "_"
AUDIT_TIMESTAMP = "Timestamps"
AUDIT_TRAIL = "audit"
AUDIT_INFO = "info"
AUDIT_INFO_TAG = "audit_info"
AUDIT_FINDING = "findings"
AUDIT_FINDING_TAG = "audit_finding"
DEFAULT_FILTERS_YAML = "default_filter.yaml"
OUTPUT_YAML_FILE = "thor_filter.yaml"
YAML_FILTERS = "filters"
DEFAULT_LEVELS = ["Alert", "Warning", "Notice", "Info"]
