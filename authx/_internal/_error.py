from typing import Any, Coroutine, Optional, Type

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from authx import exceptions


class _ErrorHandler:
    """Base Handler for FastAPI handling AuthX exceptions"""

    def __init__(self) -> None:
        """Base Handler for FastAPI handling AuthX exceptions"""

        self.MSG_DEFAULT = "AuthX Error"
        self.MSG_TOKEN_ERROR = "Token Error"
        self.MSG_MISSING_TOKEN_ERROR = "Missing JWT in request"
        self.MSG_MISSING_CSRF_ERROR = "Missing CSRF double submit token in request"
        self.MSG_TOKEN_TYPE_ERROR = "Bad token type"
        self.MSG_REVOKED_TOKEN_ERROR = "Invalid token"
        self.MSG_TOKEN_REQUIRED_ERROR = "Token required"
        self.MSG_FRESH_TOKEN_REQUIRED_ERROR = "Fresh token required"
        self.MSG_ACCESS_TOKEN_REQUIRED_ERROR = "Access token required"
        self.MSG_REFRESH_TOKEN_REQUIRED_ERROR = "Refresh token required"
        self.MSG_CSRF_ERROR = "CSRF double submit does not match"
        self.MSG_DECODE_JWT_ERROR = "Invalid Token"

    def _error_handler(
        self,
        exception: Type[exceptions.AuthXException],
        status_code: int,
        message: Optional[str] = None,
    ) -> Coroutine[Any, Any, JSONResponse]:
        """Generate the async function to be decorated by `FastAPI.exception_handler` decorator

        Args:
            exception (Type[exceptions.AuthXException]): Exception type to handle with such function.
            status_code (int): Status code relative to such exception.
            message (Optional[str], optional): Default message. Defaults to None.

        Returns:
            Coroutine[Any, Any, JSONResponse]: Async function to be decorated by `FastAPI.exception_handler` decorator.
        """

        async def _error_handler(request: Request, exc: exception):
            msg = exc.args[0] if message is None else message
            return JSONResponse(
                status_code=status_code,
                content={"message": msg, "error_type": exception.__name__},
            )

        return _error_handler

    def _set_app_exception_handler(
        self,
        app: FastAPI,
        exception: Type[exceptions.AuthXException],
        status_code: int,
        message: str,
    ) -> None:
        app.exception_handler(exception)(
            self._error_handler(exception, status_code, message)
        )

    def handle_errors(self, app: FastAPI) -> None:
        """Add the `FastAPI.exception_handlers` relative to AuthX exceptions

        Args:
            app (FastAPI): the FastAPI application to handle errors for
        """
        self._set_app_exception_handler(
            app, exception=exceptions.JWTDecodeError, status_code=422, message=None
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.MissingTokenError,
            status_code=401,
            message=self.MSG_MISSING_TOKEN_ERROR,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.MissingCSRFTokenError,
            status_code=401,
            message=self.MSG_MISSING_CSRF_ERROR,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.TokenTypeError,
            status_code=401,
            message=self.MSG_TOKEN_TYPE_ERROR,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.RevokedTokenError,
            status_code=401,
            message=self.MSG_REVOKED_TOKEN_ERROR,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.TokenRequiredError,
            status_code=401,
            message=self.MSG_TOKEN_REQUIRED_ERROR,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.FreshTokenRequiredError,
            status_code=401,
            message=self.MSG_FRESH_TOKEN_REQUIRED_ERROR,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.AccessTokenRequiredError,
            status_code=401,
            message=self.MSG_ACCESS_TOKEN_REQUIRED_ERROR,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.RefreshTokenRequiredError,
            status_code=401,
            message=self.MSG_REFRESH_TOKEN_REQUIRED_ERROR,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.CSRFError,
            status_code=401,
            message=self.MSG_CSRF_ERROR,
        )
