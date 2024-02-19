import logging
from unittest.mock import patch

from authx._internal._logger import (
    _build_log_msg,
    get_logger,
    log_debug,
    log_error,
    log_info,
    set_log_level,
)


def test_get_logger():
    logger = get_logger()
    assert isinstance(logger, logging.Logger)


def test_set_log_level():
    logger = set_log_level(logging.DEBUG)
    assert logger.getEffectiveLevel() == logging.DEBUG


def test_log_debug(caplog):
    log_debug("Debug message")
    assert "Debug message" in caplog.text
    assert logging.getLevelName(caplog.records[0].levelno) == "DEBUG"


def test_log_info(caplog):
    log_info("Info message")
    assert "Info message" in caplog.text
    assert logging.getLevelName(caplog.records[0].levelno) == "INFO"


def test_log_error(caplog):
    with patch("traceback.format_exc") as mock_format_exc:
        mock_format_exc.return_value = "Traceback"
        log_error("Error message", e=Exception("Test exception"))
        assert "Error message" in caplog.text
        assert "Traceback" in caplog.text
        assert logging.getLevelName(caplog.records[0].levelno) == "ERROR"


def test_build_log_msg_no_loc_or_method():
    result = _build_log_msg("Test message")
    assert result == "Test message"


def test_build_log_msg_with_loc():
    result = _build_log_msg("Test message", loc="test_location")
    assert result == "[test_location] Test message"


def test_build_log_msg_with_method():
    result = _build_log_msg("Test message", method="test_method")
    assert result == "[None][test_method] Test message"


def test_build_log_msg_with_loc_and_method():
    result = _build_log_msg("Test message", loc="test_location", method="test_method")
    assert result == "[test_location][test_method] [test_location] Test message"
