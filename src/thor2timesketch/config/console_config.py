from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.align import Align
from rich.table import Table


class ConsoleConfig:
    LEVELS = {
        "DEBUG": 1,
        "INFO": 2,
        "SUCCESS": 3,
        "WARNING": 5,
        "ERROR": 8,
    }
    min_level = LEVELS["INFO"]

    console = Console(force_terminal=True)
    LEVEL_STYLES = {
        "DEBUG": "magenta",
        "INFO": "green",
        "SUCCESS": "bold green",
        "WARNING": "yellow",
        "ERROR": "bold red",
    }

    @staticmethod
    def timestamp() -> str:
        return datetime.now().strftime("%d %b %Y %H:%M:%S")

    @classmethod
    def _print(cls, level: str, message: str) -> None:
        if cls.LEVELS[level] < cls.min_level:
            return
        table = Table(show_header=False, box=None)
        table.add_column("timestamp", style=cls.LEVEL_STYLES[level], min_width=20)
        table.add_column("level", style=cls.LEVEL_STYLES[level], min_width=9)
        table.add_column("message", style=cls.LEVEL_STYLES[level])
        ts = cls.timestamp()
        table.add_row(ts, f"[{level}]", message)
        cls.console.print(table, markup=True, highlight=False)

    @classmethod
    def info(cls, message: str) -> None:
        cls._print("INFO", message)

    @classmethod
    def debug(cls, message: str) -> None:
        cls._print("DEBUG", message)

    @classmethod
    def warning(cls, message: str) -> None:
        cls._print("WARNING", message)

    @classmethod
    def error(cls, message: str) -> None:
        cls._print("ERROR", message)

    @classmethod
    def success(cls, message: str) -> None:
        cls._print("SUCCESS", message)

    @classmethod
    def panel(cls, msg: str, title: str = "thor2ts", style: str = "blue") -> None:
        cls.console.print(
            Panel(
                Align(msg, align="center"),
                title=title,
                style=style,
                box=box.ASCII2,
                expand=True,
            )
        )

    @classmethod
    def set_verbose(cls, verbose: bool) -> None:
        cls.min_level = cls.LEVELS["DEBUG"] if verbose else cls.LEVELS["INFO"]
