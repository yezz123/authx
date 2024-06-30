import json
from typing import Type

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


async def create_exception_route(app: FastAPI, exception: Type[Exception]):
    @app.get("/")
    async def route():
        raise exception


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception,status_code,message,expected_message",
    [
        (exc.TokenError, 401, None, _ErrorHandler.MSG_TOKEN_ERROR),
        (
            exc.MissingTokenError,
            401,
            None,
            _ErrorHandler.MSG_MISSING_TOKEN_ERROR,
        ),
        (
            exc.MissingCSRFTokenError,
            401,
            None,
            _ErrorHandler.MSG_MISSING_CSRF_ERROR,
        ),
        (exc.TokenTypeError, 401, None, _ErrorHandler.MSG_TOKEN_TYPE_ERROR),
        (
            exc.RevokedTokenError,
            401,
            None,
            _ErrorHandler.MSG_REVOKED_TOKEN_ERROR,
        ),
        (
            exc.TokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_TOKEN_REQUIRED_ERROR,
        ),
        (
            exc.FreshTokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_FRESH_TOKEN_REQUIRED_ERROR,
        ),
        (
            exc.AccessTokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_ACCESS_TOKEN_REQUIRED_ERROR,
        ),
        (
            exc.RefreshTokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_REFRESH_TOKEN_REQUIRED_ERROR,
        ),
        (exc.CSRFError, 401, None, _ErrorHandler.MSG_CSRF_ERROR),
        (exc.JWTDecodeError, 422, None, _ErrorHandler.MSG_DECODE_JWT_ERROR),
        (exc.AuthXException, 500, "Custom message", "Custom message"),
    ],
)
async def test_set_app_exception_handler(
    app, client, error_handler, exception, status_code, message, expected_message
):
    error_handler._set_app_exception_handler(app, exception, status_code, message)

    await create_exception_route(app, exception)

    response = client.get("/")

    assert response.status_code == status_code
    assert response.json() == {
        "message": expected_message,
        "error_type": exception.__name__,
    }
