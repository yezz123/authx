import json

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse

from authx import AuthX, RequestToken, TokenPayload
from authx.config import AuthXConfig
from authx.exceptions import AuthXException, MissingTokenError


@pytest.fixture(scope="function")
def authx():
    authx = AuthX()
    authx._config.JWT_SECRET_KEY = "SECRET"
    authx._config.JWT_TOKEN_LOCATION = ["headers", "json", "cookies"]
    return authx


@pytest.fixture(scope="function")
def mock_request():
    return Request(
        scope={
            "type": "http",
            "headers": [],
            "method": "GET",
        }
    )


@pytest.fixture(scope="function")
def mock_response():
    return JSONResponse(content={})


@pytest.fixture(scope="function")
def access_token(authx: AuthX):
    return authx.create_access_token(uid="hello", fresh=True)


@pytest.fixture(scope="function")
def refresh_token(authx: AuthX):
    return authx.create_refresh_token(uid="hello")


def test_create_access_token(authx: AuthX):
    token = authx.create_access_token(uid="blablah", fresh=True)
    assert isinstance(token, str)
    payload = authx._decode_token(token, verify=False)
    assert payload.fresh
    assert payload.sub == "blablah"
    assert payload.type == "access"


def test_create_refresh_token(authx: AuthX):
    token = authx.create_refresh_token(uid="blablah", fresh=True)
    assert isinstance(token, str)
    payload = authx._decode_token(token, verify=False)
    assert payload.fresh is not True
    assert payload.sub == "blablah"
    assert payload.type == "refresh"


def test_verify_token(authx: AuthX):
    token = authx.create_access_token(uid="blablah", fresh=True)
    payload = authx._decode_token(token, verify=False)
    request_token = RequestToken(
        token=token, csrf=None, location="headers", type="access"
    )
    payload = authx.verify_token(request_token, verify_csrf=False)
    assert payload.fresh
    assert payload.sub == "blablah"


def test_set_wrong_token_type_cookie_exception(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    token = authx.create_access_token(uid="blablah", fresh=True)

    with pytest.raises(ValueError):
        authx._set_cookies(token=token, type="bad_type", response=response)


def test_unset_wrong_token_type_cookie_exception(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    token = authx.create_access_token(uid="blablah", fresh=True)
    authx.set_access_cookies(token=token, response=response)

    with pytest.raises(ValueError):
        authx._unset_cookies(type="bad_type", response=response)


def test_set_access_cookies(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    token = authx.create_access_token(uid="blablah", fresh=True)
    authx.set_access_cookies(token, response=response)

    assert all(
        cookie.startswith(authx.config.JWT_ACCESS_COOKIE_NAME)
        or cookie.startswith(authx.config.JWT_ACCESS_CSRF_COOKIE_NAME)
        for cookie in response.headers.getlist("set-cookie")
    )


def test_set_refresh_cookies(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    token = authx.create_refresh_token(uid="blablah", fresh=True)
    authx.set_refresh_cookies(token, response=response)

    assert all(
        cookie.startswith(authx.config.JWT_REFRESH_COOKIE_NAME)
        or cookie.startswith(authx.config.JWT_REFRESH_CSRF_COOKIE_NAME)
        for cookie in response.headers.getlist("set-cookie")
    )


def test_unset_access_cookies(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    authx.unset_access_cookies(response=response)

    assert all(
        cookie.startswith(f'{authx.config.JWT_ACCESS_COOKIE_NAME}=""')
        or cookie.startswith(f'{authx.config.JWT_ACCESS_CSRF_COOKIE_NAME}=""')
        for cookie in response.headers.getlist("set-cookie")
    )


def test_unset_refresh_cookies(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    authx.unset_refresh_cookies(response=response)

    assert all(
        cookie.startswith(f'{authx.config.JWT_REFRESH_COOKIE_NAME}=""')
        or cookie.startswith(f'{authx.config.JWT_REFRESH_CSRF_COOKIE_NAME}=""')
        for cookie in response.headers.getlist("set-cookie")
    )


def test_unset_cookies(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    authx.unset_cookies(response=response)

    assert all(
        cookie.startswith(f'{authx.config.JWT_REFRESH_COOKIE_NAME}=""')
        or cookie.startswith(f'{authx.config.JWT_REFRESH_CSRF_COOKIE_NAME}=""')
        or cookie.startswith(f'{authx.config.JWT_ACCESS_COOKIE_NAME}=""')
        or cookie.startswith(f'{authx.config.JWT_ACCESS_CSRF_COOKIE_NAME}=""')
        for cookie in response.headers.getlist("set-cookie")
    )


@pytest.mark.asyncio
async def test_get_token_from_request_without_auth(authx: AuthX):
    req = Request(
        scope={
            "method": "GET",
            "type": "http",
            "headers": [],
        }
    )
    with pytest.raises(MissingTokenError):
        await authx._get_token_from_request(
            request=req, refresh=False, locations=["headers"]
        )


@pytest.mark.asyncio
async def test_get_token_from_request_access(authx: AuthX, access_token: str):
    req = Request(
        scope={
            "method": "GET",
            "type": "http",
            "headers": [[b"authorization", f"Bearer {access_token}".encode()]],
        }
    )
    request_token = await authx.get_access_token_from_request(request=req)
    assert request_token.token == access_token
    assert request_token.location == "headers"
    assert request_token.csrf is None
    assert request_token.type == "access"


@pytest.mark.asyncio
async def test_get_token_from_request_refresh(authx: AuthX, refresh_token: str):
    req = Request(
        scope={
            "method": "GET",
            "type": "http",
            "headers": [
                [
                    b"cookie",
                    f"{authx.config.JWT_REFRESH_COOKIE_NAME}={refresh_token};".encode(),
                ]
            ],
        }
    )
    request_token = await authx.get_refresh_token_from_request(request=req)
    assert request_token.token == refresh_token
    assert request_token.location == "cookies"
    assert request_token.csrf is None
    assert request_token.type == "refresh"


@pytest.mark.asyncio
async def test__auth_required(authx: AuthX, refresh_token: str, access_token: str):
    req = Request(
        scope={
            "method": "GET",
            "type": "http",
            "headers": [
                [b"content-type", b"application/json"],
                [b"authorization", f"Bearer {access_token}".encode()],
                [
                    b"cookie",
                    f"{authx.config.JWT_REFRESH_COOKIE_NAME}={refresh_token};".encode(),
                ],
            ],
        }
    )

    refresh_token: TokenPayload = await authx._auth_required(
        request=req, verify_fresh=False, type="refresh"
    )
    assert refresh_token.type == "refresh"
    access_token: TokenPayload = await authx._auth_required(
        request=req, verify_fresh=True, type="access"
    )
    assert access_token.type == "access"


@pytest.mark.asyncio
async def test_token_required(authx: AuthX, access_token: str):
    req = Request(
        scope={
            "method": "GET",
            "type": "http",
            "headers": [
                [b"content-type", b"application/json"],
                [b"authorization", f"Bearer {access_token}".encode()],
                [
                    b"cookie",
                    f"{authx.config.JWT_REFRESH_COOKIE_NAME}={refresh_token};".encode(),
                ],
            ],
        }
    )

    dependency = authx.token_required(verify_fresh=True, type="access")
    access_token: TokenPayload = await dependency(request=req)
    assert access_token.type == "access"


def test_load_config(authx):
    new_config = AuthXConfig(JWT_SECRET_KEY="NEW_SECRET")
    authx.load_config(new_config)
    assert authx.config.JWT_SECRET_KEY == "NEW_SECRET"


@pytest.mark.asyncio
async def test_get_token_from_request_optional(authx, mock_request):
    token = await authx._get_token_from_request(mock_request, optional=True)
    assert token is None


@pytest.mark.asyncio
async def test_get_token_from_request_not_optional(authx, mock_request):
    with pytest.raises(MissingTokenError):
        await authx._get_token_from_request(mock_request, optional=False)


def test_create_refresh_token_with_custom_data(authx):
    custom_data = {"role": "admin"}
    token = authx.create_access_token(uid="test_user", data=custom_data)
    payload = authx._decode_token(token, verify=False)
    payload_dict = json.loads(payload.json())
    assert payload_dict.get("role") == "admin"


def test_verify_token_with_csrf(authx):
    token = authx.create_access_token(uid="test_user")
    request_token = RequestToken(
        token=token, csrf="test_csrf", location="cookies", type="access"
    )

    with pytest.raises(AuthXException):
        authx.verify_token(request_token, verify_csrf=True)


def test_set_and_unset_cookies(authx, mock_response):
    access_token = authx.create_access_token(uid="test_user")
    refresh_token = authx.create_refresh_token(uid="test_user")

    authx.set_access_cookies(access_token, mock_response)
    authx.set_refresh_cookies(refresh_token, mock_response)

    assert (
        len(mock_response.headers.getlist("set-cookie")) == 4
    )  # 2 for access, 2 for refresh

    authx.unset_cookies(mock_response)

    assert (
        len(mock_response.headers.getlist("set-cookie")) == 8
    )  # 4 additional for unsetting


def test_token_required_dependency(authx):
    dependency = authx.token_required(type="access", verify_fresh=True)
    assert callable(dependency)
