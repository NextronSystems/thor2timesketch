import typer
from typing import Optional
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.config.filter_creator import FilterCreator
from thor2timesketch.transformation.json_transformer import JsonTransformer
from thor2timesketch.output.output_writer import OutputWriter
from thor2timesketch.exceptions import Thor2tsError

app = typer.Typer(
    help="Convert THOR security scanner logs to Timesketch format",
    no_args_is_help=True,
    add_completion=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _show_version(value: bool) -> None:
    if value:
        try:
            tool_version = version("thor2timesketch")
        except PackageNotFoundError:
            tool_version = "unknown (development)"
        ConsoleConfig.info(f"thor2ts version: `{tool_version}`")
        raise typer.Exit()


def _validate_args(
    input_file: Optional[Path],
    output_file: Optional[Path],
    sketch: Optional[str],
    filter_path: Optional[Path],
    generate_filters: bool,
) -> None:
    allowed = {
        frozenset(["generate_filters"]),
        frozenset(["input_file", "generate_filters"]),
        frozenset(["input_file", "output_file"]),
        frozenset(["input_file", "sketch"]),
        frozenset(["input_file", "output_file", "filter"]),
        frozenset(["input_file", "sketch", "filter"]),
    }

    active = set()
    if input_file:
        active.add("input_file")
    if generate_filters:
        active.add("generate_filters")
    if output_file:
        active.add("output_file")
    if sketch:
        active.add("sketch")
    if filter_path:
        active.add("filter")

    if active not in allowed:
        ConsoleConfig.error("Check -h for valid arguments")
        raise typer.Exit(code=1)


def _filter_generation(input_file: Optional[Path]) -> None:
    try:
        FilterCreator(input_file).generate_yaml_file()
    except Thor2tsError as e:
        ConsoleConfig.error(f"{e}")
        raise typer.Exit(code=1)


@app.command()
def main(
    input_file: Optional[Path] = typer.Argument(
        None, help="Path to the THOR file", metavar="[THOR JSON LOGS]"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Write converted THOR logs to specified JSONL file"
    ),
    sketch: Optional[str] = typer.Option(
        None,
        "--sketch",
        "-s",
        help="Sketch ID or name for ingesting THOR logs into Timesketch",
    ),
    filter_path: Optional[Path] = typer.Option(
        None, "--filter", "-F", help="Path to a YAML filter configuration file"
    ),
    generate_filters: bool = typer.Option(
        False,
        "--generate-filters",
        help="Generate a default filters YAML file with name 'thor_filter.yaml'",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose debugging output"
    ),
    _version: bool = typer.Option(
        False,
        "--version",
        callback=_show_version,
        is_eager=True,
        help="thor2ts version",
    ),
) -> None:
    ConsoleConfig.panel(
        "Convert THOR security scanner logs to Timesketch format",
        title="thor2ts powered by Nextron Systems",
        style="bold green",
    )

    ConsoleConfig.set_verbose(verbose)
    _validate_args(input_file, output_file, sketch, filter_path, generate_filters)

    if generate_filters:
        _filter_generation(input_file)
        raise typer.Exit()

    if not input_file:
        ConsoleConfig.error("Input file is required")
        raise typer.Exit(code=1)
    try:
        events = JsonTransformer().transform_thor_logs(input_file, filter_path)
        OutputWriter(input_file, output_file, sketch).write(events)
        ConsoleConfig.success("✓ thor2ts successfully completed")
    except Thor2tsError as e:
        ConsoleConfig.error(f"{e}")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        ConsoleConfig.warning("⚠ Processing interrupted by user")
        raise typer.Exit(code=130)
    except Exception as e:
        ConsoleConfig.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)
