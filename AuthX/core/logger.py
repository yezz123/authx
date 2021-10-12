import logging
import logging.handlers

from AuthX.core.config import DEBUG


class LevelFilter:
    """
    Create a logger with the given name.
    """

    def __init__(self, level):
        """
        Initialize the instance.

        Args:
            level (int): The level to filter on.
        """
        self._level = level

    def filter(self, log_record):
        """
        Filter the log record.

        Args:
            log_record (logging.LogRecord): The log record to filter.

        Returns:
            bool: True if the record should be logged, False otherwise.
        """
        return log_record.levelno == self._level


logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(message)s")

if DEBUG:
    """
        Log to console
    """
    log_info = logging.handlers.TimedRotatingFileHandler(
        "logs/info.log", when="midnight", backupCount=7
    )
else:
    """
        Log to file
    """
    log_info = logging.StreamHandler()

log_info.addFilter(LevelFilter(logging.INFO))  # type: ignore

log_info.setFormatter(formatter)

logger.addHandler(log_info)
