from typing import Type

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from authx import exceptions
from authx._internal import _ErrorHandler


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def error_handler():
    return _ErrorHandler()


@pytest.fixture
def client(app):
    return TestClient(app)


def create_exception_route(app: FastAPI, exception: Type[Exception]):
    @app.get(f"/{exception.__name__}")
    async def route():
        raise exception()


@pytest.mark.asyncio
async def test_error_handler_initialization(error_handler):
    assert isinstance(error_handler, _ErrorHandler)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception,status_code,message,expected_message",
    [
        (exceptions.TokenError, 401, None, _ErrorHandler.MSG_TOKEN_ERROR),
        (
            exceptions.MissingTokenError,
            401,
            None,
            _ErrorHandler.MSG_MISSING_TOKEN_ERROR,
        ),
        (
            exceptions.MissingCSRFTokenError,
            401,
            None,
            _ErrorHandler.MSG_MISSING_CSRF_ERROR,
        ),
        (exceptions.TokenTypeError, 401, None, _ErrorHandler.MSG_TOKEN_TYPE_ERROR),
        (
            exceptions.RevokedTokenError,
            401,
            None,
            _ErrorHandler.MSG_REVOKED_TOKEN_ERROR,
        ),
        (
            exceptions.TokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_TOKEN_REQUIRED_ERROR,
        ),
        (
            exceptions.FreshTokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_FRESH_TOKEN_REQUIRED_ERROR,
        ),
        (
            exceptions.AccessTokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_ACCESS_TOKEN_REQUIRED_ERROR,
        ),
        (
            exceptions.RefreshTokenRequiredError,
            401,
            None,
            _ErrorHandler.MSG_REFRESH_TOKEN_REQUIRED_ERROR,
        ),
        (exceptions.CSRFError, 401, None, _ErrorHandler.MSG_CSRF_ERROR),
        (exceptions.JWTDecodeError, 422, None, _ErrorHandler.MSG_DECODE_JWT_ERROR),
        (exceptions.AuthXException, 500, "Custom message", "Custom message"),
    ],
)
async def test_set_app_exception_handler(
    app, client, error_handler, exception, status_code, message, expected_message
):
    create_exception_route(app, exception)
    error_handler._set_app_exception_handler(app, exception, status_code, message)

    response = await client.get(f"/{exception.__name__}")
    assert response.status_code == status_code
    assert response.json() == {
        "message": expected_message,
        "error_type": exception.__name__,
    }


@pytest.mark.asyncio
async def test_custom_exception_message(app, client, error_handler):
    class CustomException(exceptions.AuthXException):
        pass

    create_exception_route(app, CustomException)
    error_handler._set_app_exception_handler(app, CustomException, 418, None)

    @app.get("/custom_message")
    async def custom_message_route():
        raise CustomException("Custom exception message")

    response = await client.get("/custom_message")
    assert response.status_code == 418
    assert response.json() == {
        "message": "Custom exception message",
        "error_type": "CustomException",
    }


def test_default_message_fallback(app, client, error_handler):
    class FallbackException(exceptions.AuthXException):
        pass

    create_exception_route(app, FallbackException)
    error_handler._set_app_exception_handler(app, FallbackException, 500, None)

    response = client.get("/FallbackException")
    assert response.status_code == 500
    assert response.json() == {
        "message": _ErrorHandler.MSG_DEFAULT,
        "error_type": "FallbackException",
    }


def test_multiple_exceptions(app, client, error_handler):
    error_handler._set_app_exception_handler(app, exceptions.TokenError, 401, None)
    error_handler._set_app_exception_handler(app, exceptions.CSRFError, 403, None)

    create_exception_route(app, exceptions.TokenError)
    create_exception_route(app, exceptions.CSRFError)

    response_token = client.get("/TokenError")
    assert response_token.status_code == 401
    assert response_token.json()["message"] == _ErrorHandler.MSG_TOKEN_ERROR

    response_csrf = client.get("/CSRFError")
    assert response_csrf.status_code == 403
    assert response_csrf.json()["message"] == _ErrorHandler.MSG_CSRF_ERROR


@pytest.mark.asyncio
async def test_error_handler_method(error_handler):
    class TestException(exceptions.AuthXException):
        pass

    response = await error_handler._error_handler(
        None, TestException(), 400, "Test message"
    )
    assert response.status_code == 400
    assert response.body == b'{"message":"Test message","error_type":"TestException"}'


@pytest.mark.asyncio
async def test_error_handler_method_no_message(error_handler):
    class TestException(exceptions.AuthXException):
        pass

    response = await error_handler._error_handler(
        None, TestException("Custom arg"), 400, None
    )
    assert response.status_code == 400
    assert response.body == b'{"message":"Custom arg","error_type":"TestException"}'
