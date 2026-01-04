import json

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

import authx.exceptions as exc
from authx import AuthX
from authx._internal import _ErrorHandler


@pytest.fixture(scope="function")
def authx():
    return AuthX()


@pytest.fixture(scope="function")
def app():
    return FastAPI()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(scope="class")
def error_handler():
    return _ErrorHandler()


@pytest.mark.asyncio
async def test_error_handler(authx: AuthX):
    error_handler = authx._error_handler(
        request=Request(scope={"type": "http", "method": "GET"}),
        exc=ValueError(),
        status_code=100,
        message="Sample Message",
    )
    resp = await error_handler

    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 100
    assert json.loads(resp.body.decode()) == {
        "message": "Sample Message",
        "error_type": ValueError.__name__,
    }


@pytest.mark.asyncio
async def test_error_handler_without_message(authx: AuthX):
    error_handler = authx._error_handler(
        request=Request(scope={"type": "http", "method": "GET"}),
        exc=ValueError("Execution Message"),
        status_code=100,
        message=None,
    )
    resp = await error_handler

    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 100
    assert json.loads(resp.body.decode()) == {
        "message": "Execution Message",
        "error_type": ValueError.__name__,
    }


def test_handle_app_errors(app: FastAPI, authx: AuthX):
    authx.handle_errors(app)

    assert exc.JWTDecodeError in app.exception_handlers
    assert exc.MissingTokenError in app.exception_handlers
    assert exc.MissingCSRFTokenError in app.exception_handlers
    assert exc.TokenTypeError in app.exception_handlers
    assert exc.RevokedTokenError in app.exception_handlers
    assert exc.TokenRequiredError in app.exception_handlers
    assert exc.FreshTokenRequiredError in app.exception_handlers
    assert exc.AccessTokenRequiredError in app.exception_handlers
    assert exc.RefreshTokenRequiredError in app.exception_handlers
    assert exc.CSRFError in app.exception_handlers


def test_invalid_token_init():
    errors = ["Invalid signature", "Expired token"]
    exception = exc.InvalidToken(errors)
    assert exception.errors == errors


async def create_exception_route(app: FastAPI, exception: type[Exception]):
    @app.get("/")
    async def route():
        raise exception


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception,status_code,message,expected_message",
    [
        (exc.TokenError, 401, None, _ErrorHandler.MSG_TokenError),
        (
            exc.MissingTokenError,
            401,
            None,
            _ErrorHandler.MSG_MissingTokenError,
        ),
        (exc.TokenTypeError, 401, None, _ErrorHandler.MSG_TokenTypeError),
        (
            exc.RevokedTokenError,
            401,
            None,
            _ErrorHandler.MSG_RevokedTokenError,
        ),
        (
            exc.TokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_TokenRequiredError,
        ),
        (
            exc.FreshTokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_FreshTokenRequiredError,
        ),
        (
            exc.AccessTokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_AccessTokenRequiredError,
        ),
        (
            exc.RefreshTokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_RefreshTokenRequiredError,
        ),
        (exc.CSRFError, 401, None, _ErrorHandler.MSG_CSRFError),
        (exc.JWTDecodeError, 422, None, _ErrorHandler.MSG_JWTDecodeError),
        (exc.AuthXException, 500, "Custom message", "Custom message"),
    ],
)
async def test_set_app_exception_handler(app, client, error_handler, exception, status_code, message, expected_message):
    error_handler._set_app_exception_handler(app, exception, status_code, message)

    await create_exception_route(app, exception)

    response = client.get("/")

    assert response.status_code == status_code
    assert response.json() == {
        "message": expected_message,
        "error_type": exception.__name__,
    }


@pytest.mark.asyncio
async def test_missing_csrf_token_error_shows_detailed_message(app, client, error_handler):
    """Test that MissingCSRFTokenError shows detailed exception message (fixes #720).

    This ensures users get helpful guidance when they encounter CSRF errors,
    including how to use set_access_cookies or disable CSRF protection.
    """
    detailed_message = (
        "Missing CSRF token. Expected in 'X-CSRF-TOKEN' header. "
        "Ensure you're using 'set_access_cookies'/'set_refresh_cookies' to set cookies "
        "(which also sets the CSRF cookie), then include the CSRF token from that cookie "
        "in your request header. To disable CSRF protection, set JWT_COOKIE_CSRF_PROTECT=False."
    )

    # Create a route that raises MissingCSRFTokenError with detailed message
    @app.get("/csrf-error")
    async def csrf_error_route():
        raise exc.MissingCSRFTokenError(detailed_message)

    # Register the handler with message=None so it uses the exception message
    error_handler._set_app_exception_handler(app, exc.MissingCSRFTokenError, 401, None)

    response = client.get("/csrf-error")

    assert response.status_code == 401
    response_json = response.json()
    assert response_json["error_type"] == "MissingCSRFTokenError"
    # The detailed message should be preserved
    assert response_json["message"] == detailed_message
    assert "set_access_cookies" in response_json["message"]
    assert "JWT_COOKIE_CSRF_PROTECT=False" in response_json["message"]
