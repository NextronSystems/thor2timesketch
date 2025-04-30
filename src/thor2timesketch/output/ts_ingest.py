import os.path
import time
from typing import Dict, Union, Any, Iterator
from rich.progress import Progress, TextColumn, SpinnerColumn
from timesketch_import_client import importer
from timesketch_api_client import config as timesketch_config
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch import constants
from thor2timesketch.exceptions import TimesketchError

logger = LoggerConfig.get_logger(__name__)

class TSIngest:


    def __init__(self, thor_file: str, sketch: str) -> None:
        self.thor_file = thor_file
        self.ts_client = timesketch_config.get_client()
        if self.ts_client is None:
            raise TimesketchError("Failed to connect to Timesketch client. Check your configuration.")
        self.timeline_name: str = self._get_timeline_name(thor_file)
        sketch_type: Union[int, str] = self._identify_sketch_type(sketch)
        self.my_sketch: Any = self._load_sketch(sketch_type)


    def _get_timeline_name(self, thor_file: str) -> str:
        file_basename: str = os.path.basename(thor_file)
        file_name, _ = os.path.splitext(file_basename)
        return file_name

    def _identify_sketch_type(self, sketch: str) -> Union[int, str]:
        return int(sketch) if sketch.isdigit() else sketch

    def _get_available_sketches(self) -> Dict[str, int]:
        sketches = {}
        try:
            for scope in constants.TS_SCOPE:
                for sketch in self.ts_client.list_sketches(scope=scope, include_archived=False):
                    sketches[sketch.name] = int(sketch.id)
            return sketches
        except TimesketchError as error:
            error_msg = f"fFailed to retrieve sketches from Timesketch: {error}"
            logger.error(error_msg)
            raise TimesketchError(error_msg)

    def _load_sketch(self, sketch: Union[int, str]) -> Any:
        try:
            sketches = self._get_available_sketches()

            if isinstance(sketch, int):
                if sketch in sketches.values():
                    my_sketch = self.ts_client.get_sketch(sketch)
                    logger.info(f"Found sketch with ID {sketch}: {my_sketch.name}")
                    return my_sketch
                sketch = f"Sketch_{sketch}"

            elif isinstance(sketch, str):
                if sketch in sketches.keys():
                    my_sketch = self.ts_client.get_sketch(sketches[sketch])
                    logger.info(f"Found sketch with name '{sketch}': ID {my_sketch.id}")
                    return my_sketch

            logger.info("Creating a new sketch with name '{}'".format(sketch))
            my_sketch = self.ts_client.create_sketch(sketch, "New sketch created by thor2ts")
            if not my_sketch or not hasattr(my_sketch, "id"):
                raise TimesketchError("Failed to create sketch with name '{sketch}'")
            logger.info(f"New sketch has been created with name: '{my_sketch.name}' and ID: {my_sketch.id}")
            return my_sketch
        except Exception as error:
            error_msg = f"Failed to load sketch: {error}"
            logger.error(error_msg)
            raise TimesketchError(error_msg)

    def ingest_events(self, events: Iterator[Dict[str, Any]]) -> None:

        try:
            self.ts_client.get_sketch(self.my_sketch.id)
        except Exception:
            TimesketchError(f"Sketch ID `{self.my_sketch.id}` not found, aborting ingest")

        processed_count = 0
        error_count = 0

        with Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                TextColumn("[cyan]{task.completed} processed"),
                TextColumn("• [red]{task.fields[errors]} errors"),
                transient=True
        ) as progress:
            task = progress.add_task(
                f"[bold green]Ingesting to sketch '{self.my_sketch.name}'",
                total=None,
                completed=0,
                errors=0,
                sketch_name=self.my_sketch.name
            )
            try:
                with importer.ImportStreamer() as streamer:
                    streamer.set_sketch(self.my_sketch)
                    streamer.set_timeline_name(self.timeline_name)
                    streamer.set_provider("thor2ts")
                    streamer.set_upload_context(self.timeline_name)

                    for event in events:
                        try:
                            streamer.add_dict(event)
                            processed_count += 1
                        except Exception as e:
                            error_count += 1
                            logger.debug(f"Error adding event to streamer: '{e}'")
                        finally:
                            progress.update(task, completed=processed_count, errors=error_count)
                if not streamer.timeline:
                    raise TimesketchError("Error creating timeline, ingestion may have failed")

                progress.update(task, description="[bold yellow]Indexing timeline…")
                deadline = time.time() + 60
                timeout_reached = False
                while streamer.state.lower() not in ("ready", "success") and not timeout_reached:
                    if time.time() > deadline:
                        logger.warning("Indexing did not complete within 60 seconds - the timeline will continue to be indexed in the background")
                        timeout_reached = True
                    time.sleep(1)
                if not timeout_reached:
                    progress.update(task, description="[bold green]Indexing complete")

            except KeyboardInterrupt:
                logger.warning("Timesketch ingestion interrupted by user")
                raise
            except Exception as error:
                error_msg = f"Failed to ingest events: {error}"
                logger.error(error_msg)
                raise TimesketchError(error_msg)

        logger.info(f"Processed {processed_count} events for sketch '{self.my_sketch.name}'")
        if error_count > 0:
            logger.warning(f"Encountered {error_count} errors during ingestion")