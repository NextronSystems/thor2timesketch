import os
import json
from typing import Dict, Generator

from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.progress_bar import ProgressBar


logger = LoggerConfig.get_logger(__name__)


class THOROutputToFile:
    def __init__(self, output_file: str, progress_bar: ProgressBar):
        self.output_file = output_file
        self.progress_bar = progress_bar
        self._prepare_output_dir()
        self.mode = 'a' if os.path.exists(self.output_file) else 'w'

    def _validate_output_file(self)  -> None:
        try:
            if not self.output_file.lower().endswith('.jsonl'):
                original = self.output_file
                output_file = os.path.splitext(self.output_file)[0] + '.jsonl'
                logger.info(f"Changed output file from `{original}` to `{output_file}` to ensure JSONL format")
        except Exception as e:
            logger.error("Error validating or modifying the output file: %s", e)

    def _prepare_output_dir(self) -> None:
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.isdir(output_dir):
            try:
                logger.info(f"Creating output directory: {output_dir}")
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create output directory `{output_dir}`: {e}")

    def write_to_file(self, events: Generator[Dict[str, any], None, None]) -> None:
        self._validate_output_file()
        self._prepare_output_dir()
        with open(self.output_file, self.mode, encoding='utf-8') as file:
            for event in events:
                try:
                    file.write(json.dumps(event) + "\n")
                    self.progress_bar.update(1)
                except Exception as e:
                    logger.error("Error writing event: %s", e)
        logger.info("Successfully written events to %s", self.output_file)
        self.progress_bar.close()
