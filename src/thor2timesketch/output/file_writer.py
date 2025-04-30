import os
import json
from typing import Dict, Any, Iterator
from thor2timesketch.config.logger import LoggerConfig
from rich.progress import Progress, TextColumn, SpinnerColumn
from thor2timesketch import constants
from thor2timesketch.exceptions import OutputError

logger = LoggerConfig.get_logger(__name__)


class FileWriter:
    def __init__(self, output_file: str):
        self.output_file = output_file


    def _normalize_extension(self, path: str) -> str:
        file_name, extension = os.path.splitext(path)
        if extension.lower() != constants.OUTPUT_FILE_EXTENSION:
            path = file_name + constants.OUTPUT_FILE_EXTENSION
            logger.info(f"Changed output file to '{path}' to ensure 'JSONL' format")
        return path

    def _prepare_output_dir(self) -> None:
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: '{output_dir}'")
            except Exception as e:
                logger.error(f"Failed to create output directory {output_dir}`: {e}")
                raise OutputError(f"Cannot create output directory: {e}")

    def _cleanup_file(self, output_file:str)-> None:
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                logger.debug(f"Removed output file: '{output_file}'")
            except OSError as e:
                logger.error(f"Failed to remove output file: {e}")
                raise OutputError(f"Cannot remove output file: {e}")

    def write_to_file(self, events: Iterator[Dict[str, Any]]) -> None:
        self.output_file = self._normalize_extension(self.output_file)
        self._prepare_output_dir()
        mode = 'a' if os.path.exists(self.output_file) else 'w'
        action = "Appending to" if mode == 'a' else "Writing to"
        logger.info(f"'{action}' file: '{self.output_file}'")
        try:
            processed_count = 0
            error_count = 0
            output_filename = os.path.basename(self.output_file)
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold green]Writing to '{task.fields[filename]}'"),
                    TextColumn("[green]{task.completed} processed"),
                    TextColumn("• [red]{task.fields[errors]} errors"),
                    transient=True
            ) as progress:
                task = progress.add_task(
                    "Writing", total=None, completed=0, errors=0,
                    filename=output_filename
                )

                with open(self.output_file, mode, encoding=constants.DEFAULT_ENCODING) as file:
                    for event in events:
                        try:
                            file.write(json.dumps(event) + "\n")
                            processed_count += 1
                        except Exception as e:
                            error_count += 1
                            if error_count <= constants.MAX_WRITE_ERRORS:
                                logger.error(f"Error writing event to file: {e}")
                        finally:
                            progress.update(task, completed=processed_count, errors=error_count)

            if error_count > 0:
                logger.error(f"Encountered '{error_count}' errors while writing '{processed_count}' events")
                self._cleanup_file(self.output_file)
                raise OutputError(f"File processing failed with {error_count} errors")
            else:
                logger.info(f"Successfully wrote '{processed_count}' events to '{self.output_file}'")


        except KeyboardInterrupt:
            logger.warning("Process interrupted by user")
            self._cleanup_file(self.output_file)
            raise

        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            self._cleanup_file(self.output_file)
            raise OutputError(str(e))