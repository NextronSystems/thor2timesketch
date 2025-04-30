import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

class LoggerConfig:
    custom_theme = Theme({
        "logging.level.debug": "blue",
        "logging.level.info": "green",
        "logging.level.warning": "yellow",
        "logging.level.error": "red"
    })

    console = Console(theme=custom_theme)

    @classmethod
    def setup_root_logger(cls, level: int = logging.INFO) -> None:
        handler = RichHandler(
            console=cls.console,
            rich_tracebacks=True,
            show_path=False,
            markup=True,
            show_time=True,
            show_level=True,
            enable_link_path=False,
            log_time_format="%y-%m-%d %H:%M:%S"
        )

        logging.basicConfig(
            level=level,
            format="%(message)s",
            handlers=[handler]
        )

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)