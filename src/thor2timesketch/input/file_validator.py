from pathlib import Path
from typing import Sequence, Union
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.constants import EMPTY_FILE
from thor2timesketch.exceptions import (
    FileNotFound,
    FileNotReadableError,
    EmptyFileError,
    InvalidFileExtensionError,
)


class FileValidator:
    def __init__(self, valid_extensions: Sequence[str]) -> None:
        self.valid_extensions = {ext.lower() for ext in valid_extensions}

    def validate_file(self, file_path: Union[str, Path]) -> Path:
        file_path = Path(file_path)
        self._check_file_exists(file_path)
        self._check_file_readable(file_path)
        self._check_file_not_empty(file_path)
        self._check_file_extension(file_path)
        return file_path

    def _check_file_exists(self, file_path: Path) -> None:
        if not file_path.is_file():
            raise FileNotFound(f"File '{file_path}' does not exist.")
        ConsoleConfig.debug(f"File '{file_path}' is found")

    def _check_file_readable(self, file_path: Path) -> None:
        try:
            with file_path.open("rb"):
                pass
        except OSError as e:
            raise FileNotReadableError(
                f"File '{file_path}' is not readable: {e}"
            ) from e
        ConsoleConfig.debug(f"File '{file_path}' has read permissions.")

    def _check_file_not_empty(self, file_path: Path) -> None:
        if file_path.stat().st_size == EMPTY_FILE:
            raise EmptyFileError(f"File '{file_path}' is empty.")
        ConsoleConfig.debug(f"File '{file_path}' is not empty.")

    def _check_file_extension(self, file_path: Path) -> None:
        ext = file_path.suffix.lower()
        if ext not in self.valid_extensions:
            expected = ", ".join(self.valid_extensions)
            error_msg = (
                f"Invalid file extension for '{file_path}'. "
                f"Expected one of: ['{expected}'], but got: '{ext!r}'"
            )
            raise InvalidFileExtensionError(error_msg)
        ConsoleConfig.debug(f"File '{file_path}' has a valid extension: '{ext}'")
