import json

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import authx.exceptions as exc
from authx import AuthX


@pytest.fixture(scope="function")
def authx():
    return AuthX()


@pytest.fixture(scope="function")
def app():
    return FastAPI()


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
