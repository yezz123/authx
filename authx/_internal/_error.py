from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from authx import exceptions


class _ErrorHandler:
    """Base Handler for FastAPI handling AuthX exceptions."""

    MSG_TokenError = "Token Error"
    MSG_MissingTokenError = "Missing JWT in request"
    MSG_MissingCSRFTokenError = "Missing CSRF double submit token in request"
    MSG_TokenTypeError = "Bad token type"
    MSG_RevokedTokenError = "Invalid token"
    MSG_TokenRequiredError = "Token required"
    MSG_FreshTokenRequiredError = "Fresh token required"
    MSG_AccessTokenRequiredError = "Access token required"
    MSG_RefreshTokenRequiredError = "Refresh token required"
    MSG_CSRFError = "CSRF double submit does not match"
    MSG_JWTDecodeError = "Invalid Token"

    async def _error_handler(
        self,
        request: Request,
        exc: exceptions.AuthXException,
        status_code: int,
        message: Optional[str],
    ) -> JSONResponse:
        """Generate the async function to be decorated by `FastAPI.exception_handler` decorator.

        Args:
            request (Request): The request object.
            exc (exceptions.AuthXException): Exception object.
            status_code (int): HTTP status code.
            message (str): Default message.

        Returns:
            JSONResponse: The JSON response.
        """
        if message is None:
            default_message = str(exc)
            attr_name = f"MSG_{exc.__class__.__name__}"
            message = getattr(self, attr_name, default_message)

        return JSONResponse(
            status_code=status_code,
            content={
                "message": message,
                "error_type": exc.__class__.__name__,
            },
        )

    def _set_app_exception_handler(
        self,
        app: FastAPI,
        exception: type[exceptions.AuthXException],
        status_code: int,
        message: Optional[str],
    ) -> None:
        async def exception_handler_wrapper(request: Request, exc: exceptions.AuthXException) -> JSONResponse:
            return await self._error_handler(request, exc, status_code, message)

        # Add the exception handler to the FastAPI application
        # The exception handler will be called when the specified exception is raised, and the status code and message will be returned
        # The exception handler will return a JSONResponse with the specified status code and message
        app.exception_handler(exception)(exception_handler_wrapper)

    def handle_errors(self, app: FastAPI) -> None:
        """Add the `FastAPI.exception_handlers` relative to AuthX exceptions.

        Args:
            app (FastAPI): the FastAPI application to handle errors for
        """
        self._set_app_exception_handler(app, exception=exceptions.JWTDecodeError, status_code=422, message=None)
        self._set_app_exception_handler(
            app,
            exception=exceptions.MissingTokenError,
            status_code=401,
            message=self.MSG_TokenError,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.MissingCSRFTokenError,
            status_code=401,
            message=self.MSG_MissingCSRFTokenError,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.TokenTypeError,
            status_code=401,
            message=self.MSG_TokenTypeError,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.RevokedTokenError,
            status_code=401,
            message=self.MSG_RevokedTokenError,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.TokenRequiredError,
            status_code=401,
            message=self.MSG_TokenRequiredError,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.FreshTokenRequiredError,
            status_code=401,
            message=self.MSG_FreshTokenRequiredError,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.AccessTokenRequiredError,
            status_code=401,
            message=self.MSG_AccessTokenRequiredError,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.RefreshTokenRequiredError,
            status_code=401,
            message=self.MSG_RefreshTokenRequiredError,
        )
        self._set_app_exception_handler(
            app,
            exception=exceptions.CSRFError,
            status_code=401,
            message=self.MSG_CSRFError,
        )
