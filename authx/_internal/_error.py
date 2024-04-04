from typing import Optional, Type

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from authx import exceptions


class _ErrorHandler:
    """Base Handler for FastAPI handling AuthX exceptions"""

    MSG_DEFAULT = "AuthX Error"
    MSG_TOKEN_ERROR = "Token Error"
    MSG_MISSING_TOKEN_ERROR = "Missing JWT in request"
    MSG_MISSING_CSRF_ERROR = "Missing CSRF double submit token in request"
    MSG_TOKEN_TYPE_ERROR = "Bad token type"
    MSG_REVOKED_TOKEN_ERROR = "Invalid token"
    MSG_TOKEN_REQUIRED_ERROR = "Token required"
    MSG_FRESH_TOKEN_REQUIRED_ERROR = "Fresh token required"
    MSG_ACCESS_TOKEN_REQUIRED_ERROR = "Access token required"
    MSG_REFRESH_TOKEN_REQUIRED_ERROR = "Refresh token required"
    MSG_CSRF_ERROR = "CSRF double submit does not match"
    MSG_DECODE_JWT_ERROR = "Invalid Token"

    async def _error_handler(
        self,
        request: Request,
        exc: exceptions.AuthXException,
        status_code: int,
        message: str,
    ) -> JSONResponse:
        """Generate the async function to be decorated by `FastAPI.exception_handler` decorator

        Args:
            request (Request): The request object.
            exc (exceptions.AuthXException): Exception object.
            status_code (int): HTTP status code.
            message (str): Default message.

        Returns:
            JSONResponse: The JSON response.
        """
        msg = exc.args[0] if message is None else message
        return JSONResponse(
            status_code=status_code,
            content={"message": msg, "error_type": exc.__class__.__name__},
        )

    def _set_app_exception_handler(
        self,
        app: FastAPI,
        exception: Type[exceptions.AuthXException],
        status_code: int,
        message: Optional[str],
    ) -> None:
        app.exception_handler(exception)(
            lambda request, exc=exception: self._error_handler(
                request, exc, status_code, message or self.MSG_DEFAULT
            )
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
