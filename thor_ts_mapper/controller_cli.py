import argparse
import os
import logging
from typing import Dict

from thor_ts_mapper.thor_input_reader import THORJSONInputReader
from thor_ts_mapper.thor_json_flattener import JSONFlattener
from thor_ts_mapper.thor_json_log_version import THORJSONLogVersionMapper
from thor_ts_mapper.thor_output_writer import THORJSONOutputWriter
from thor_ts_mapper.logger_config import LoggerConfig
from tqdm import tqdm

logger = LoggerConfig.get_logger(__name__)


class MainControllerCLI:
    @staticmethod
    def parse_arguments() -> Dict[str, str]:
        parser = argparse.ArgumentParser(
            description="THOR-TS-Mapper converts THOR security scanner logs into Timesketch-compatible format."
        )
        parser.add_argument("input_file", help="Path to THOR JSON file", nargs="?")
        parser.add_argument(
            "-o",
            dest="output_file",
            help="Output file path (default:<input_file>_mapped.jsonl)",
            default=None
        )
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {__import__('thor_ts_mapper').__version__}",
            help="Show the version number and exit"
        )
        args = parser.parse_args()

        if args.verbose:
            LoggerConfig.setup_root_logger(level=logging.DEBUG)
        else:
            LoggerConfig.setup_root_logger(level=logging.INFO)

        if args.input_file is None:
            logger.error("Input file is required unless --version is specified")
            exit(1)

        if args.output_file:
            if not str(args.output_file).lower().endswith('.jsonl'):
                original = args.output_file
                args.output_file = f"{os.path.splitext(args.output_file)[0]}.jsonl"
                logger.info(f"Changed output file from '{original}' to '{args.output_file}' to ensure JSONL format")
        else:
            input_file_name = os.path.splitext(args.input_file)[0]
            args.output_file = f"{input_file_name}_mapped.jsonl"

        output_dir = os.path.dirname(args.output_file)
        if output_dir and not os.path.isdir(output_dir):
            logger.info(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)

        return {
            "input_file": args.input_file,
            "output_file": args.output_file,
            "verbose": args.verbose
        }

    @staticmethod
    def run():
        args = MainControllerCLI.parse_arguments()
        input_file = args["input_file"]
        output_file = args["output_file"]

        file_size = os.path.getsize(input_file)
        logger.info(f"Processing input file: {input_file} ({file_size / 1024:.2f} KB)")

        success, thor_logs = THORJSONInputReader.get_valid_json(input_file)
        if not success:
            logger.error("Failed to open or read input file.")
            exit(1)

        flattener = JSONFlattener()
        output_writer = THORJSONOutputWriter(output_file)
        events_processed = 0
        try:
            with tqdm(total=None, unit=' events', desc='Mapping THOR logs') as pbar:
                for json_line in thor_logs:

                    flattened_json = flattener.flatten_jsonl(json_line)
                    mapper = THORJSONLogVersionMapper.get_mapper(flattened_json)
                    mapped_events = mapper.map_thor_events(flattened_json)

                    if mapped_events:
                        output_writer.write_mapped_logs(mapped_events)
                        events_processed += len(mapped_events)
                        pbar.update(1)
                        pbar.set_postfix({"mapped": events_processed})

            output_writer.get_logs_written_summary()
            logger.info(f"Nextron’s mission continues -> we detect hackers <-. Launch Timesketch and ingest THOR logs via Web UI or CLI and let the hunt begin.")
        except Exception as e:
            logger.error(f"Error processing THOR logs: {e}")
            exit(1)
        finally:
            output_writer.close()


if __name__ == "__main__":
    MainControllerCLI.run()