from typing import Iterator, Dict, Any, Optional

from thor2timesketch.exceptions import OutputError, TimesketchError
from thor2timesketch.output.file_writer import FileWriter
from thor2timesketch.output.ts_ingest import TSIngest
from pathlib import Path


class OutputWriter:
    def __init__(
        self,
        input_file: Path,
        output_file: Optional[Path] = None,
        sketch: Optional[str] = None,
    ) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.sketch = sketch

    def write(self, events: Iterator[Dict[str, Any]]) -> None:
        try:
            if self.output_file:
                try:
                    FileWriter(self.output_file).write_to_file(events)
                except OutputError:
                    raise
            if self.sketch:
                try:
                    TSIngest(self.input_file, self.sketch).ingest_events(events)
                except TimesketchError:
                    raise
        except Exception as e:
            raise OutputError(f"Unexpected error during output writing: {e}") from e
