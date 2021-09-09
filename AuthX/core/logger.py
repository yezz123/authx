import logging
import logging.handlers


class LevelFilter:
    def __init__(self, level):
        self._level = level

    def filter(self, log_record):
        return log_record.levelno == self._level


logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(message)s")


log_info = logging.StreamHandler()


log_info.addFilter(LevelFilter(logging.INFO))  # type: ignore

log_info.setFormatter(formatter)

logger.addHandler(log_info)
