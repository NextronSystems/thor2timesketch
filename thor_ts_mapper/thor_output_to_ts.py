import os.path
from typing import Dict, Union
from alive_progress import alive_bar
from timesketch_import_client import importer
from timesketch_api_client import config as timesketch_config
from thor_ts_mapper.logger_config import LoggerConfig


logger = LoggerConfig.get_logger(__name__)

class THORIngestToTS:

    TS_SCOPE = ['user', 'shared']

    def __init__(self, thor_file: str, sketch: Union[int, str] = None):
        self.ts_client = timesketch_config.get_client()
        self.timeline_name = self._get_timeline_name(thor_file)
        self.my_sketch = self._load_sketch(sketch)

    def _get_timeline_name(self, thor_file) -> str:
            return os.path.splitext(os.path.basename(thor_file))[0]

    def _get_available_sketches(self) -> Dict[str, int]:
        sketches = {}
        for scope in self.TS_SCOPE:
            for sketch in self.ts_client.list_sketches(scope=scope, include_archived=False):
                sketches[sketch.name] = int(sketch.id)
        return sketches


    def _load_sketch(self, sketch: Union[int, str] = None):

        sketches = self._get_available_sketches()

        if isinstance(sketch, int):
            if sketch in sketches.values():
                my_sketch = self.ts_client.get_sketch(sketch)
                logger.info(f"Found sketch with ID {sketch}: {my_sketch.name}")
                return my_sketch
            else:
                sketch = f"Sketch_{sketch}"

        elif isinstance(sketch, str):
            if sketch in sketches.keys():
                my_sketch = self.ts_client.get_sketch(sketches[sketch])
                logger.info(f"Found sketch with name '{sketch}': ID {my_sketch.id}")
                return my_sketch

        logger.info("Creating a new sketch with name '{}'".format(sketch))
        my_sketch = self.ts_client.create_sketch(sketch, "New sketch created by thor2ts")
        logger.info(f"New sketch has been created with name: '{my_sketch.name}' and ID: {my_sketch.id}")
        return my_sketch


    def ingest_events(self, events) -> None:
        with alive_bar(spinner='dots', title=f"Ingesting to sketch '{self.my_sketch.name}'") as bar:
            with importer.ImportStreamer() as streamer:
                streamer.set_sketch(self.my_sketch)
                streamer.set_timeline_name(self.timeline_name)
                streamer.set_upload_context(self.timeline_name)
                for event in events:
                    try:
                        streamer.add_dict(event)
                        bar()
                    except Exception as e:
                        logger.error("Error adding event to streamer: %s", e)
            logger.info(f"Successfully ingested events into sketch '{self.my_sketch.name}'")
            logger.info("The timeline will continue to be indexed in the background")