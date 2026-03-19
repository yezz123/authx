from unittest.mock import AsyncMock, Mock, call

from fastapi import Response

from authx import AuthXDependency


class MockAuthX:
    def __init__(self):
        self.create_access_token = Mock(return_value="access_token")
        self.create_refresh_token = Mock(return_value="refresh_token")
        self.set_access_cookies = Mock()
        self.set_refresh_cookies = Mock()
        self.unset_access_cookies = Mock()
        self.unset_refresh_cookies = Mock()
        self.unset_cookies = Mock()
        self.get_current_subject = AsyncMock(return_value="current_subject")


async def test_authx_dependency_properties():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)

    dep = AuthXDependency(authx, request, response)

    assert dep.request is request
    assert dep.response is response


async def test_create_access_token_delegates():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    result = dep.create_access_token("uid", fresh=True)

    assert result == "access_token"
    authx.create_access_token.assert_called_once_with("uid", True, None, None, None, None)


async def test_create_refresh_token_delegates():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    result = dep.create_refresh_token("uid")

    assert result == "refresh_token"
    authx.create_refresh_token.assert_called_once_with("uid", None, None, None, None)


async def test_set_access_cookies_delegates():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    dep.set_access_cookies("tok123")

    authx.set_access_cookies.assert_called_once_with(token="tok123", response=response, max_age=None)


async def test_set_access_cookies_with_custom_response():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    custom_response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    dep.set_access_cookies("tok123", response=custom_response, max_age=3600)

    authx.set_access_cookies.assert_called_once_with(token="tok123", response=custom_response, max_age=3600)


async def test_set_refresh_cookies_delegates():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    dep.set_refresh_cookies("refresh_tok")

    authx.set_refresh_cookies.assert_called_once_with(token="refresh_tok", response=response, max_age=None)


async def test_unset_access_cookies_delegates():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    dep.unset_access_cookies()

    authx.unset_access_cookies.assert_called_once_with(response=response)
    authx.unset_refresh_cookies.assert_not_called()


async def test_unset_refresh_cookies_delegates():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    dep.unset_refresh_cookies()

    authx.unset_refresh_cookies.assert_called_once_with(response=response)
    authx.unset_access_cookies.assert_not_called()


async def test_unset_refresh_cookies_with_custom_response():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    custom_response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    dep.unset_refresh_cookies(response=custom_response)

    authx.unset_refresh_cookies.assert_called_once_with(response=custom_response)


async def test_unset_cookies_delegates():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    dep.unset_cookies()

    authx.unset_cookies.assert_called_once_with(response=response)


async def test_get_current_subject_delegates():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    result = await dep.get_current_subject()

    assert result == "current_subject"
    authx.get_current_subject.assert_called_once_with(request=request)


async def test_unset_access_and_refresh_are_independent():
    """Verify unset_access_cookies and unset_refresh_cookies call different underlying methods."""
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)
    dep = AuthXDependency(authx, request, response)

    dep.unset_access_cookies()
    dep.unset_refresh_cookies()

    assert authx.unset_access_cookies.call_args_list == [call(response=response)]
    assert authx.unset_refresh_cookies.call_args_list == [call(response=response)]
