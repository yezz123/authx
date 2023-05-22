import json
from typing import Any, Coroutine, Dict, List

import pytest
from fastapi import Request

from authx import AuthXConfig
from authx.core import (
    _get_token_from_cookies,
    _get_token_from_headers,
    _get_token_from_json,
    _get_token_from_query,
    _get_token_from_request,
)
from authx.exceptions import MissingCSRFTokenError, MissingTokenError


@pytest.fixture(scope="function")
def config() -> AuthXConfig:
    config = AuthXConfig()
    config.JWT_ALGORITHM = "HS256"
    config.JWT_SECRET_KEY = "4321J4OP3JIB12BJ4NKJF2EBJE2"
    config.JWT_TOKEN_LOCATION = ["headers", "cookies", "json", "query"]
    config.JWT_CSRF_METHODS = ["POST", "DELETE", "PUT"]
    config.JWT_REFRESH_CSRF_HEADER_NAME = "X-REFRESH-CSRF-TOKEN"
    return config


@pytest.fixture(scope="function")
def request_headers(config: AuthXConfig) -> List[List[str]]:
    return [
        [
            f"{config.JWT_HEADER_NAME.lower()}".encode(),
            f"{config.JWT_HEADER_TYPE} TOKEN".encode(),
        ]
    ]


@pytest.fixture(scope="function")
def request_csrf_headers(config: AuthXConfig) -> List[List[str]]:
    return [
        [
            f"{config.JWT_ACCESS_CSRF_HEADER_NAME.lower()}".encode(),
            b"ACCESS_CSRF_TOKEN",
        ],
        [
            f"{config.JWT_REFRESH_CSRF_HEADER_NAME.lower()}".encode(),
            b"REFRESH_CSRF_TOKEN",
        ],
    ]


@pytest.fixture(scope="function")
def request_cookies(config: AuthXConfig) -> List[List[str]]:
    return [
        [b"content-type", b"application/json"],
        [
            b"cookie",
            f"{config.JWT_ACCESS_COOKIE_NAME}=TOKEN; {config.JWT_REFRESH_COOKIE_NAME}=REFRESH_TOKEN;".encode(),
        ],
    ]


@pytest.fixture(scope="function")
def request_query(config: AuthXConfig) -> Dict[str, str]:
    return {f"{config.JWT_QUERY_STRING_NAME}": "TOKEN"}


@pytest.fixture(scope="function")
def request_body(config: AuthXConfig) -> Coroutine[Any, Any, Dict[str, Any]]:
    async def receiver():
        return {
            "type": "http.request",
            "body": json.dumps(
                {
                    config.JWT_JSON_KEY: "TOKEN",
                    config.JWT_REFRESH_JSON_KEY: "REFRESH_TOKEN",
                }
            ).encode(),
        }

    return receiver


@pytest.fixture(scope="function")
def http_request(request_body, request_headers, request_cookies, request_csrf_headers, request_query) -> Request:
    return Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [*request_headers, *request_cookies, *request_csrf_headers],
            "query_string": request_query,
        },
        receive=request_body,
    )


@pytest.mark.asyncio
async def test_get_token_from_query(config: AuthXConfig, request_query: Dict[str, str]):
    req = Request(
        scope={
            "type": "http",
            "query_string": request_query,
        }
    )

    request_token = await _get_token_from_query(request=req, config=config)
    assert request_token is not None
    assert request_token.type == "access"
    assert request_token.location == "query"
    assert request_token.token == "TOKEN"


@pytest.mark.asyncio
async def test_get_token_from_query_with_exception(config: AuthXConfig):
    req = Request(
        scope={
            "type": "http",
            "query_string": {},
        }
    )

    with pytest.raises(MissingTokenError):
        await _get_token_from_query(request=req, config=config)


@pytest.mark.asyncio
async def test_get_token_from_headers(config: AuthXConfig, request_headers: List[List[str]]):
    req = Request(
        scope={
            "type": "http",
            "headers": [*request_headers],
        }
    )

    request_token = await _get_token_from_headers(request=req, config=config)
    assert request_token is not None
    assert request_token.type == "access"
    assert request_token.location == "headers"
    assert request_token.token == "TOKEN"


@pytest.mark.asyncio
async def test_get_token_from_headers_without_header_type(config: AuthXConfig):
    config.JWT_HEADER_TYPE = None
    req = Request(
        scope={
            "type": "http",
            "headers": [
                [
                    f"{config.JWT_HEADER_NAME.lower()}".encode(),
                    b"TOKEN",
                ]
            ],
        }
    )

    request_token = await _get_token_from_headers(request=req, config=config)
    assert request_token is not None
    assert request_token.type == "access"
    assert request_token.location == "headers"
    assert request_token.token == "TOKEN"

    config.JWT_HEADER_TYPE = "Bearer"


@pytest.mark.asyncio
async def test_get_token_from_headers_with_token_exception(config: AuthXConfig):
    req = Request(scope={"type": "http", "headers": []})

    with pytest.raises(MissingTokenError):
        await _get_token_from_headers(request=req, config=config)


@pytest.mark.asyncio
async def test_get_token_from_cookies_get(config: AuthXConfig, request_cookies: List[List[str]]):
    req = Request(
        scope={
            "method": "GET",
            "type": "http",
            "headers": [*request_cookies],
        }
    )

    # Test on GET with Access Token
    request_token = await _get_token_from_cookies(request=req, config=config)
    assert request_token is not None
    assert request_token.type == "access"
    assert request_token.location == "cookies"
    assert request_token.token == "TOKEN"
    # Test on GET with Refresh Token
    request_token = await _get_token_from_cookies(request=req, config=config, refresh=True)
    assert request_token is not None
    assert request_token.type == "refresh"
    assert request_token.location == "cookies"
    assert request_token.token == "REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_get_token_from_cookies_post(
    config: AuthXConfig,
    request_cookies: List[List[str]],
    request_csrf_headers: List[List[str]],
):
    # Test on POST
    req = Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [*request_cookies, *request_csrf_headers],
        }
    )

    request_token = await _get_token_from_cookies(request=req, config=config)
    assert request_token is not None
    assert request_token.type == "access"
    assert request_token.location == "cookies"
    assert request_token.csrf == "ACCESS_CSRF_TOKEN"
    assert request_token.token == "TOKEN"

    request_token = await _get_token_from_cookies(request=req, config=config, refresh=True)
    assert request_token is not None
    assert request_token.type == "refresh"
    assert request_token.location == "cookies"
    assert request_token.csrf == "REFRESH_CSRF_TOKEN"
    assert request_token.token == "REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_get_token_from_cookies_post_without_csrf_exception(
    config: AuthXConfig, request_cookies: list[list[str]]
):
    config.JWT_COOKIE_CSRF_PROTECT = False
    # Test on POST
    req = Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [*request_cookies],
        }
    )

    request_token = await _get_token_from_cookies(request=req, config=config)
    assert request_token is not None
    assert request_token.location == "cookies"
    assert request_token.token == "TOKEN"
    config.JWT_COOKIE_CSRF_PROTECT = True


@pytest.mark.asyncio
async def test_get_token_from_cookies_post_with_csrf_exception(config: AuthXConfig, request_cookies: list[list[str]]):
    # Test on POST
    req = Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [*request_cookies],
        }
    )
    with pytest.raises(MissingCSRFTokenError):
        await _get_token_from_cookies(request=req, config=config)


@pytest.mark.asyncio
async def test_get_token_from_cookies_post_with_missing_token_exception(
    config: AuthXConfig,
):
    # Test on POST
    req = Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [],
        }
    )
    with pytest.raises(MissingTokenError):
        await _get_token_from_cookies(request=req, config=config)


@pytest.mark.asyncio
async def test_get_token_from_json_post_content_type_exception(
    config: AuthXConfig,
    request_body: Coroutine[Any, Any, dict[Dict, Any]],
):
    # Test on POST
    req = Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [],
        },
        receive=request_body,
    )

    with pytest.raises(MissingTokenError):
        await _get_token_from_json(request=req, config=config)


@pytest.mark.asyncio
async def test_get_token_from_json_post(
    config: AuthXConfig,
    request_body: Coroutine[Any, Any, dict[Dict, Any]],
):
    # Test on POST
    req = Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [[b"content-type", b"application/json"]],
        },
        receive=request_body,
    )

    request_token = await _get_token_from_json(request=req, config=config)
    assert request_token is not None
    assert request_token.type == "access"
    assert request_token.location == "json"
    assert request_token.csrf is None
    assert request_token.token == "TOKEN"

    request_token = await _get_token_from_json(request=req, config=config, refresh=True)
    assert request_token is not None
    assert request_token.type == "refresh"
    assert request_token.location == "json"
    assert request_token.csrf is None
    assert request_token.token == "REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_get_token_from_json_post_with_exception(
    config: AuthXConfig,
):
    async def void_receiver():
        return {
            "type": "http.request",
            "body": json.dumps({}).encode(),
        }

    # Test on POST
    req = Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [[b"content-type", b"application/json"]],
        },
        receive=void_receiver,
    )

    with pytest.raises(MissingTokenError):
        await _get_token_from_json(request=req, config=config)


@pytest.mark.asyncio
async def test_get_token_from_json_post_with_bad_data_exception(
    config: AuthXConfig,
):
    async def bad_receiver():
        return {
            "type": "http.request",
            "body": json.dumps(
                {
                    config.JWT_JSON_KEY: lambda: 124,
                }
            ).encode(),
        }

    # Test on POST
    req = Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [[b"content-type", b"application/json"]],
        },
        receive=bad_receiver,
    )

    with pytest.raises(MissingTokenError):
        await _get_token_from_json(request=req, config=config)


@pytest.mark.asyncio
async def test_get_token_from_request(http_request: Request, config: AuthXConfig):
    request_token = await _get_token_from_request(request=http_request, config=config)
    assert request_token is not None
    assert request_token.type == "access"
    assert request_token.location == "headers"
    assert request_token.csrf is None
    assert request_token.token == "TOKEN"


@pytest.mark.asyncio
async def test_get_token_from_request_with_exception(config: AuthXConfig):
    req = Request(
        scope={
            "method": "POST",
            "type": "http",
            "headers": [],
            "query_string": {},
        },
        receive=request_body,
    )
    with pytest.raises(MissingTokenError):
        await _get_token_from_request(request=req, config=config)


@pytest.mark.asyncio
async def test_get_token_from_request_with_locations(http_request: Request, config: AuthXConfig):
    request_token = await _get_token_from_request(
        request=http_request, config=config, locations=["query"], refresh=True
    )
    assert request_token is not None
    assert request_token.type == "access"
    assert request_token.location == "query"
    assert request_token.csrf is None
    assert request_token.token == "TOKEN"

    request_token = await _get_token_from_request(request=http_request, config=config, locations=["json"], refresh=True)
    assert request_token is not None
    assert request_token.type == "refresh"
    assert request_token.location == "json"
    assert request_token.csrf is None
    assert request_token.token == "REFRESH_TOKEN"

    request_token = await _get_token_from_request(
        request=http_request, config=config, locations=["cookies", "json"], refresh=True
    )
    assert request_token is not None
    assert request_token.type == "refresh"
    assert request_token.location == "cookies"
    assert request_token.csrf == "REFRESH_CSRF_TOKEN"
    assert request_token.token == "REFRESH_TOKEN"

    with pytest.raises(MissingTokenError):
        await _get_token_from_request(request=http_request, config=config, locations=[], refresh=True)
