import argparse
import os
import logging
import sys
from typing import Dict, Optional, Set

from thor_ts_mapper.logger_config import LoggerConfig
from thor_ts_mapper.thor_json_transformer import THORJSONTransformer
from thor_ts_mapper.thor_output_to_file import THOROutputToFile
from thor_ts_mapper.thor_output_to_ts import THORIngestToTS

logger = LoggerConfig.get_logger(__name__)


class MainControllerCLI:
    @staticmethod
    def parse_arguments() -> Dict[str, Optional[str]]:
        parser = argparse.ArgumentParser(
            description="THOR-TS-Mapper: Convert THOR security scanner logs to Timesketch format",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            "input_file",
            help="Path to THOR JSON log file"
        )
        parser.add_argument(
            "-o", "--output-file",
            dest="output_file",
            help="Write output to specified JSONL file (default: <input_file>_mapped.jsonl)",
            default=None
        )
        parser.add_argument(
            "--ts_sketch",
            help="Sketch ID or name for ingesting events into Timesketch",
            default=None
        )
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose debugging output"
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {__import__('thor_ts_mapper').__version__}",
            help="Show version number and exit"
        )

        args = parser.parse_args()

        log_level = logging.DEBUG if args.verbose else logging.INFO
        LoggerConfig.setup_root_logger(level=log_level)

        if not os.path.isfile(args.input_file):
            logger.error(f"Input file not found: {args.input_file}")
            sys.exit(1)

        return {
            "input_file": args.input_file,
            "output_file": args.output_file,
            "ts_sketch": args.ts_sketch,
            "verbose": args.verbose
        }

    @staticmethod
    def run():
        args = MainControllerCLI.parse_arguments()
        input_file = args["input_file"]
        output_file = args["output_file"]
        ts_sketch = args["ts_sketch"]

        if ts_sketch and ts_sketch.isdigit():
            ts_sketch = int(ts_sketch)

        output_to_file = output_file is not None
        output_to_ts = ts_sketch is not None

        if not (output_to_file or output_to_ts):
            logger.error("No output destination specified. Use -o/--output-file for file output or --ts_sketch for Timesketch ingestion.")
            sys.exit(1)


        try:
            mapped_events = THORJSONTransformer.transform_thor_logs(input_file)
            if output_to_file:
                write_to_file = THOROutputToFile(output_file)
                write_to_file.write_to_file(mapped_events)
            if output_to_ts:
                upload_to_ts = THORIngestToTS(thor_file=input_file, sketch=ts_sketch)
                upload_to_ts.ingest_events(mapped_events)

            logger.info("THOR log processing completed successfully")

        except KeyboardInterrupt:
            logger.warning("Processing interrupted by user")
            sys.exit(130)
        except Exception as e:
            logger.error(f"Error processing THOR logs: {e}", exc_info=args["verbose"])
            sys.exit(1)


if __name__ == "__main__":
    MainControllerCLI.run()