import json
from typing import Dict, Any, Iterator
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.utils.progress_bar import ProgressBar
from thor2timesketch.constants import (
    OUTPUT_FILE_EXTENSION,
    DEFAULT_ENCODING,
    MAX_WRITE_ERRORS,
)
from thor2timesketch.exceptions import OutputError
from pathlib import Path


class FileWriter:
    def __init__(self, output_file: Path):
        self.output_file = output_file

    def _normalize_extension(self) -> None:
        if self.output_file.suffix.lower() != OUTPUT_FILE_EXTENSION:
            self.output_file = self.output_file.with_suffix(OUTPUT_FILE_EXTENSION)
            ConsoleConfig.info(
                f"Changed output file to '{self.output_file}' to ensure JSONL format"
            )

    def _prepare_output_dir(self) -> None:
        output_dir = self.output_file.parent
        if output_dir and not output_dir.is_dir():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                ConsoleConfig.info(f"Created output directory: '{output_dir}'")
            except OSError as e:
                raise OutputError(
                    f"Failed to create output directory {output_dir}`: {e}"
                )

    def _cleanup_file(self) -> None:
        if self.output_file.exists():
            try:
                self.output_file.unlink()
                ConsoleConfig.debug(f"Removed output file: '{self.output_file}'")
            except OSError as e:
                raise OutputError(f"Failed to remove output file: {e}")

    def write_to_file(self, events: Iterator[Dict[str, Any]]) -> None:
        self._normalize_extension()
        self._prepare_output_dir()
        mode = "a" if self.output_file.exists() else "w"
        action = "Appending to " if mode == "a" else "Writing to "
        try:
            with ProgressBar(f"{action} {self.output_file.name} ...") as progress:
                with self.output_file.open(mode, encoding=DEFAULT_ENCODING) as file:
                    for event in events:
                        try:
                            file.write(json.dumps(event) + "\n")
                            progress.advance()
                        except (TypeError, ValueError, OSError) as e:
                            progress.advance(step=0, error=1)
                            if progress.errors >= MAX_WRITE_ERRORS:
                                raise OutputError(
                                    f"Too many errors encountered while writing to file: {e}"
                                ) from e

            if progress.errors:
                self._cleanup_file()
                raise OutputError(
                    f"Encountered '{progress.errors}' errors while writing '{progress.processed}' events"
                )
            ConsoleConfig.success(
                f"Successfully wrote '{progress.processed}' events to '{self.output_file}'"
            )

        except KeyboardInterrupt:
            self._cleanup_file()
            ConsoleConfig.warning(
                f"Keyboard interrupt received. File '{self.output_file}' was not written."
            )
            raise

        except Exception as e:
            self._cleanup_file()
            raise OutputError(f"Error writing to file: {e}")
