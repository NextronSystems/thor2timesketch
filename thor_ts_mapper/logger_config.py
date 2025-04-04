import logging
import colorlog
from typing import Optional, Dict


class LoggerConfig:

    DEFAULT_FORMAT = '%(log_color)s%(asctime)s - %(levelname)s - %(message)s'
    DEFAULT_COLORS = {
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'DEBUG': 'blue',
    }

    @classmethod
    def setup_root_logger(cls, level: int = logging.INFO,
                          format_str: Optional[str] = None,
                          log_colors: Optional[Dict[str, str]] = None) -> None:
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)


        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            format_str or cls.DEFAULT_FORMAT,
            log_colors=log_colors or cls.DEFAULT_COLORS
        ))
        root_logger.addHandler(handler)

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)