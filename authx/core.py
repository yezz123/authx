"""Core functions for AuthX."""

import contextlib
from typing import Any, Literal, Optional

from fastapi import Request

from authx.config import AuthXConfig
from authx.exceptions import CSRFError, MissingCSRFTokenError, MissingTokenError
from authx.schema import RequestToken
from authx.types import TokenLocations


async def _get_token_from_headers(
    request: Request, config: AuthXConfig, refresh: bool = False, **kwargs: Any
) -> RequestToken:
    """Get access token from headers."""
    # Get Header
    auth_header: Optional[str] = request.headers.get(config.JWT_HEADER_NAME)
    if auth_header is None:
        raise MissingTokenError(f"Missing '{config.JWT_HEADER_TYPE}' in '{config.JWT_HEADER_NAME}' header.")

    if config.JWT_HEADER_TYPE:
        token = auth_header.replace(f"{config.JWT_HEADER_TYPE} ", "")
    else:
        token = auth_header

    return RequestToken(token=token, csrf=None, location="headers")


async def _get_token_from_cookies(
    request: Request, config: AuthXConfig, refresh: bool = False, **kwargs: Any
) -> RequestToken:
    """Get access token from cookies.

    Args:
        request (Request): FastAPI Request
        config (AuthXConfig): AuthX Configuration
        refresh (bool, optional): If True, get refresh token. Defaults to False.

    Raises:
        MissingTokenError: If cookie is not set
        MissingCSRFTokenError: If CSRF token is not set

    Returns:
        RequestToken: RequestToken instance
    """
    cookie_key = config.JWT_ACCESS_COOKIE_NAME
    csrf_header_key = config.JWT_ACCESS_CSRF_HEADER_NAME
    csrf_field_key = config.JWT_ACCESS_CSRF_FIELD_NAME
    if refresh:
        cookie_key = config.JWT_REFRESH_COOKIE_NAME
        csrf_header_key = config.JWT_REFRESH_CSRF_HEADER_NAME
        csrf_field_key = config.JWT_REFRESH_CSRF_FIELD_NAME

    cookie_token = request.cookies.get(cookie_key)
    if not cookie_token:
        raise MissingTokenError(f"Missing cookie '{cookie_key}'.")

    csrf_token = None
    if config.JWT_COOKIE_CSRF_PROTECT and request.method.upper() in config.JWT_CSRF_METHODS:
        csrf_token = request.headers.get(csrf_header_key.lower())
        if not csrf_token and config.JWT_CSRF_CHECK_FORM:
            form = getattr(request, "form", None)
            if form is not None and callable(form):  # pragma: no cover
                with contextlib.suppress(Exception, CSRFError):
                    form_data = await form()
                    if form_data is not None:  # pragma: no cover
                        value = form_data.get(csrf_field_key)
                        if isinstance(value, str) or value is None:
                            csrf_token = value
                        else:
                            raise ValueError("Unexpected type for csrf_token")
        if not csrf_token:
            raise MissingCSRFTokenError("Missing CSRF token")

    return RequestToken(
        token=cookie_token,
        csrf=csrf_token,
        type=("refresh" if refresh else "access"),
        location="cookies",
    )


async def _get_token_from_query(
    request: Request, config: AuthXConfig, refresh: bool = False, **kwargs: Any
) -> RequestToken:
    query_token = request.query_params.get(config.JWT_QUERY_STRING_NAME)
    if query_token is None:
        raise MissingTokenError(f"Missing '{config.JWT_QUERY_STRING_NAME}' in query parameters")

    return RequestToken(token=query_token, location="query")


async def _get_token_from_json(
    request: Request, config: AuthXConfig, refresh: bool = False, **kwargs: Any
) -> RequestToken:
    if request.headers.get("content-type") != "application/json":
        raise MissingTokenError("Invalid content-type. Must be application/json")

    key = config.JWT_JSON_KEY
    token_type: Literal["access", "refresh"] = "access"
    if refresh:
        token_type = "refresh"
        key = config.JWT_REFRESH_JSON_KEY

    try:
        json_data: dict[str, Any] = await request.json()
        json_token = json_data.get(key)
        if isinstance(json_token, str):
            return RequestToken(
                token=json_token,
                type=token_type,
                location="json",
            )
    except Exception as e:
        raise MissingTokenError("Token is not parsable") from e
    raise MissingTokenError("Missing token in json data")


TOKEN_GETTERS = {
    "json": _get_token_from_json,
    "query": _get_token_from_query,
    "cookies": _get_token_from_cookies,
    "headers": _get_token_from_headers,
}


async def _get_token_from_request(
    request: Request,
    config: AuthXConfig,
    refresh: bool = False,
    locations: Optional[TokenLocations] = None,
    **kwargs: Any,
) -> RequestToken:
    errors: list[MissingTokenError] = []

    if locations is None:
        locations = config.JWT_TOKEN_LOCATION

    for location in locations:
        try:
            getter = TOKEN_GETTERS[location]
            token = await getter(request, config, refresh, **kwargs)
            if token is not None:  # pragma: no cover
                return token
        except MissingTokenError as e:
            errors.append(e)

    if errors:
        raise MissingTokenError(*(str(err) for err in errors))
    raise MissingTokenError(f"No token found in request from '{locations}'")
