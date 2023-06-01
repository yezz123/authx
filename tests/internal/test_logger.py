import logging

from authx._internal._logger import _build_log_msg, get_logger, set_log_level


def test_get_logger():
    logger = get_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "authx"


def test_set_log_level():
    logger = get_logger()
    set_log_level("INFO")
    assert logger.level == logging.INFO


def test_build_log_msg():
    msg = _build_log_msg("Log message", loc="Location", method="Method")
    assert msg == "[Location][Method] [Location] Log message"
