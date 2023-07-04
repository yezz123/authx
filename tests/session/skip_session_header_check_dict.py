from unittest.mock import Mock

import pytest

from authx.external import SessionMiddleware


@pytest.fixture
def middleware():
    return SessionMiddleware(
        app=None, secret_key="test", skip_session_header={"header_name": "X-TESTAPI-Skip", "header_value": "skip"}
    )


def test_skip_session_header_check_dict_with_skip_header(middleware):
    request = Mock()
    request.headers = {"X-TESTAPI-Skip": "skip"}

    assert middleware.skip_session_header_check(request) is True


def test_skip_session_header_check_dict_without_skip_header(middleware):
    request = Mock()
    request.headers = {"X-Other-Header": "value"}

    assert middleware.skip_session_header_check(request) is False


def test_skip_session_header_check_dict_with_skip_header_and_different_value(middleware):
    request = Mock()
    request.headers = {"X-TESTAPI-Skip": "other"}

    assert middleware.skip_session_header_check(request) is False
