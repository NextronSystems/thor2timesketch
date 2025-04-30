from typing import Iterator, Dict, Any, Optional
from thor2timesketch.output.file_writer import FileWriter
from thor2timesketch.output.ts_ingest import TSIngest


class OutputWriter:
    def __init__(self, input_file: str, output_file: Optional[str] = None, sketch: Optional[str] = None) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.sketch = sketch

    def write(self, events: Iterator[Dict[str, Any]]) -> None:
        if self.output_file:
            FileWriter(self.output_file).write_to_file(events)
        if self.sketch:
            TSIngest(self.input_file, self.sketch).ingest_events(events)