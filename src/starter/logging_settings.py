"""
The simple and easier way to set configuration fot logging
(because distribution by pyinstaller, avoid distribution
of extra config file).
"""
import logging
import logging.handlers
from pathlib import Path

LOGGING_OUTPUT_FILE = "app_starter.log"


def set_logging_settings():
    "Set logging settings."
    handler = get_logging_handler()
    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO
    )


def get_logging_handler():
    """Settings for logging."""
    # Logging file destination
    log_destination = Path(__file__).parents[2].joinpath("app_starter.log")

    handler = logging.handlers.RotatingFileHandler(
       filename=str(log_destination),
       maxBytes=1000000,
       backupCount=3)
    # Formatter
    formatter = logging.Formatter(
       '%(asctime)s - %(name)s -line: %(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    return handler
