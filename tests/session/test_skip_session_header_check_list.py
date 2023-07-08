from unittest.mock import Mock

import pytest

from authx.external import SessionMiddleware


@pytest.fixture
def middleware():
    return SessionMiddleware(
        app=None,
        secret_key="test",
        skip_session_header=[
            {"header_name": "X-APITEST-Skip", "header_value": "skip"},
            {"header_name": "X-Another-Skip-Header", "header_value": "skip"},
        ],
    )


def test_skip_session_header_check_list_with_multiple_skip_headers(middleware):
    request1("X-APITEST-Skip", middleware)
    request1("X-Another-Skip-Header", middleware)


def request1(argument, middleware):
    request = Mock()
    request.headers = {argument: "skip"}
    assert middleware.skip_session_header_check(request) is True


def test_skip_session_header_check_list_with_multiple_headers_and_different_values(middleware):
    request2("X-APITEST-Skip", middleware)
    request2("X-Another-Skip-Header", middleware)


def request2(argument, middleware):
    request = Mock()
    request.headers = {argument: "other"}
    assert middleware.skip_session_header_check(request) is False
