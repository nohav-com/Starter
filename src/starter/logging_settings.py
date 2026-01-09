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


def get_logging_handler(log_location=None) ->\
        logging.handlers.RotatingFileHandler:
    """Settings for logging.

    Args:
    log_location = where the log is going to be stored
    """
    handler = None
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s -line: %(lineno)d - %(levelname)s - %(message)s')
    try:
        # Logging file destination
        log_destination = Path(log_location).joinpath(LOGGING_OUTPUT_FILE)\
                          if log_location else \
                          Path(__file__).parents[2].joinpath(
                              LOGGING_OUTPUT_FILE)

        if log_destination:
            handler = logging.handlers.RotatingFileHandler(
                filename=str(log_destination),
                maxBytes=1000000,
                backupCount=3)
            handler.setFormatter(formatter)
    except Exception:
        raise
    finally:
        return handler
