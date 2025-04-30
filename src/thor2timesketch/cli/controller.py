import logging
import os
from typing import Optional
from importlib.metadata import version, PackageNotFoundError
import typer
from rich.console import Console
from thor2timesketch.config.logger import LoggerConfig
from thor2timesketch.output.output_writer import OutputWriter
from thor2timesketch.transformation.json_transformer import JsonTransformer
from thor2timesketch.exceptions import Thor2tsError

app = typer.Typer(
    help="Convert THOR security scanner logs to Timesketch format",
    no_args_is_help=True,
    add_completion=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

console = Console()
logger = LoggerConfig.get_logger(__name__)

def version_callback(value: bool) -> None:
    if value:
        try:
            pkg_version = version("thor2timesketch")
        except PackageNotFoundError:
            pkg_version = "0.0.0"
        console.print(f"[bold green]thor2timesketch[/] version: [cyan]{pkg_version}[/]")
        raise typer.Exit()

@app.command()
def main(
        input_file: str = typer.Argument(..., help="Path to THOR JSON log file", metavar="INPUT_FILE"),
        output_file: Optional[str] = typer.Option(None, "--output-file", "-o",
                                                  help="Write output to specified JSONL file"),
        sketch: Optional[str] = typer.Option(None, "--sketch",
                                             help="Sketch ID or name for ingesting events into Timesketch"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose debugging output"),
        _version: bool = typer.Option(False, "--version", callback=version_callback, is_eager=True,
                                     help="Show version and exit")
) -> None:
    log_level = logging.DEBUG if verbose else logging.INFO
    LoggerConfig.setup_root_logger(level=log_level)

    if not os.path.isfile(input_file):
        logger.error(f"Input file not found: '{input_file}'. Use -h for help.")
        raise typer.Exit(code=1)

    if not (output_file or sketch):
        logger.error("Use -o/--output-file for file output or --sketch for Timesketch ingestion. Use -h for help.")
        raise typer.Exit(code=1)

    try:
        logger.info("Transforming THOR logs...")
        mapped_events = JsonTransformer().transform_thor_logs(input_json_file=input_file)

        writer = OutputWriter(input_file, output_file, sketch)
        writer.write(mapped_events)

        logger.info("✓ thor2ts successfully completed")

    except KeyboardInterrupt:
        logger.warning("⚠ Processing interrupted by user")
        raise typer.Exit(code=130)
    except Thor2tsError as e:
        logger.error(f"{e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)