import time
from pathlib import Path
from typing import Dict, Union, Any, Iterator
from timesketch_import_client import importer
from timesketch_api_client import config as timesketch_config
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.constants import TS_SCOPE
from thor2timesketch.exceptions import TimesketchError
from thor2timesketch.utils.progress_bar import ProgressBar


class TSIngest:

    def __init__(self, thor_file: Path, sketch: str) -> None:
        self.thor_file = thor_file
        self.ts_client = timesketch_config.get_client()
        if not self.ts_client:
            raise TimesketchError(
                "Failed to connect to Timesketch client. Check your configuration."
            )
        self.timeline_name: str = self.thor_file.stem
        sketch_type: Union[int, str] = self._identify_sketch_type(sketch)
        self.my_sketch: Any = self._load_sketch(sketch_type)

    def _identify_sketch_type(self, sketch: str) -> Union[int, str]:
        return int(sketch) if sketch.isdigit() else sketch

    def _get_available_sketches(self) -> Dict[str, int]:
        sketches: dict[str, int] = {}
        try:
            for scope in TS_SCOPE:
                for sketch in self.ts_client.list_sketches(
                    scope=scope, include_archived=False
                ):
                    sketches[sketch.name] = int(sketch.id)
            return sketches
        except Exception as error:
            raise TimesketchError(
                f"fFailed to retrieve sketches from Timesketch: {error}"
            )

    def _load_sketch(self, sketch: Union[int, str]) -> Any:
        try:
            available_sketches = self._get_available_sketches()

            if isinstance(sketch, int) and sketch in available_sketches.values():
                my_sketch = self.ts_client.get_sketch(sketch)
                ConsoleConfig.info(
                    f"Found sketch with ID '{sketch}': '{my_sketch.name}'"
                )
                return my_sketch

            if isinstance(sketch, str) and sketch in available_sketches.keys():
                my_sketch = self.ts_client.get_sketch(available_sketches[sketch])
                ConsoleConfig.info(
                    f"Found sketch with name '{sketch}': ID {my_sketch.id}"
                )
                return my_sketch

            ConsoleConfig.info(f"Creating a new sketch with name '{sketch}'")
            new_sketch = self.ts_client.create_sketch(str(sketch), "Created by thor2ts")
            if not new_sketch or not hasattr(new_sketch, "id"):
                raise TimesketchError(f"Failed to create sketch with name '{sketch}'")
            ConsoleConfig.info(
                f"New sketch has been created with name: '{new_sketch.name}' and ID: '{new_sketch.id}'"
            )
            return new_sketch
        except Exception as error:
            raise TimesketchError(f"Failed to load sketch: {error}")

    def ingest_events(self, events: Iterator[Dict[str, Any]]) -> None:

        try:
            self.ts_client.get_sketch(self.my_sketch.id)
        except Exception:
            raise TimesketchError(
                f"Sketch ID '{self.my_sketch.id}' not found, aborting ingest"
            )

        with ProgressBar(f"Ingesting to sketch '{self.my_sketch.name}'") as progress:
            try:
                with importer.ImportStreamer() as streamer:
                    streamer.set_sketch(self.my_sketch)
                    streamer.set_timeline_name(self.timeline_name)
                    streamer.set_provider("thor2ts")
                    streamer.set_upload_context(self.timeline_name)

                    for event in events:
                        try:
                            streamer.add_dict(event)
                            progress.advance()
                        except Exception as e:
                            progress.advance(step=0, error=1)
                            ConsoleConfig.debug(
                                f"Error adding event to streamer: '{e}'"
                            )
                if not streamer.timeline:
                    raise TimesketchError("Error creating timeline, ingestion aborted")

            except KeyboardInterrupt:
                ConsoleConfig.warning(
                    f"Keyboard interrupt received. Until this point, {progress.processed} events were ingested successfully into sketch '{self.my_sketch.name}' for timeline '{self.timeline_name}'."
                )
                raise
            except Exception as error:
                raise TimesketchError(f"Failed to ingest events: {error}")

        with ProgressBar(
            f"Indexing ingested events into sketch '{self.my_sketch.name}' this may take a few moments. Waiting on Timesketch ..."
        ) as index_progress:
            index_progress.processed = progress.processed
            index_progress.errors = progress.errors
            index_progress.progress.update(
                index_progress.task_id,
                completed=index_progress.processed,
                errors=index_progress.errors,
            )
            timeout = time.time() + 60
            timeout_reached = False
            while (
                streamer.state.lower() not in ("ready", "success")
                and not timeout_reached
            ):
                if time.time() > timeout:
                    ConsoleConfig.warning(
                        "Indexing did not complete within 60 seconds - the timeline will continue to be indexed in the background"
                    )
                    timeout_reached = True
                time.sleep(1)
            if not timeout_reached:
                index_progress.update_description(
                    f"Timeline '{self.my_sketch.name}' indexed successfully"
                )

        ConsoleConfig.success(
            f"Processed {progress.processed} events for sketch '{self.my_sketch.name}'"
        )
        if progress.errors > 0:
            ConsoleConfig.warning(
                f"Encountered {progress.errors} errors during ingestion"
            )
