import pytest
from fastapi import Request
from fastapi.responses import JSONResponse

from authx import AuthX, RequestToken, TokenPayload
from authx.exceptions import MissingTokenError


@pytest.fixture(scope="function")
def authx():
    authx = AuthX()
    authx._config.JWT_SECRET_KEY = "SECRET"
    authx._config.JWT_TOKEN_LOCATION = ["headers", "json", "cookies"]
    return authx


@pytest.fixture(scope="function")
def access_token(authx: AuthX):
    return authx.create_access_token(uid="hello", fresh=True)


@pytest.fixture(scope="function")
def refresh_token(authx: AuthX):
    return authx.create_refresh_token(uid="hello")


def test_create_access_token(authx: AuthX):
    token = authx.create_access_token(uid="ocarinow", fresh=True)
    assert isinstance(token, str)
    payload = authx._decode_token(token, verify=False)
    assert payload.fresh
    assert payload.sub == "ocarinow"
    assert payload.type == "access"


def test_create_refresh_token(authx: AuthX):
    token = authx.create_refresh_token(uid="ocarinow", fresh=True)
    assert isinstance(token, str)
    payload = authx._decode_token(token, verify=False)
    assert payload.fresh is not True
    assert payload.sub == "ocarinow"
    assert payload.type == "refresh"


def test_verify_token(authx: AuthX):
    token = authx.create_access_token(uid="ocarinow", fresh=True)
    payload = authx._decode_token(token, verify=False)
    request_token = RequestToken(token=token, csrf=None, location="headers", type="access")
    payload = authx.verify_token(request_token, verify_csrf=False)
    assert payload.fresh
    assert payload.sub == "ocarinow"


def test_set_wrong_token_type_cookie_exception(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    token = authx.create_access_token(uid="ocarinow", fresh=True)

    with pytest.raises(ValueError):
        authx._set_cookies(token=token, type="bad_type", response=response)


def test_unset_wrong_token_type_cookie_exception(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    token = authx.create_access_token(uid="ocarinow", fresh=True)
    authx.set_access_cookies(token=token, response=response)

    with pytest.raises(ValueError):
        authx._unset_cookies(type="bad_type", response=response)


def test_set_access_cookies(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    token = authx.create_access_token(uid="ocarinow", fresh=True)
    authx.set_access_cookies(token, response=response)

    assert all(
        cookie.startswith(authx.config.JWT_ACCESS_COOKIE_NAME)
        or cookie.startswith(authx.config.JWT_ACCESS_CSRF_COOKIE_NAME)
        for cookie in response.headers.getlist("set-cookie")
    )


def test_set_refresh_cookies(authx: AuthX):
    response = JSONResponse(content={"foo": "bar"})
    token = authx.create_refresh_token(uid="ocarinow", fresh=True)
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
        await authx._get_token_from_request(request=req, refresh=False, locations=["headers"])


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

    refresh_token: TokenPayload = await authx._auth_required(request=req, verify_fresh=False, type="refresh")
    assert refresh_token.type == "refresh"
    access_token: TokenPayload = await authx._auth_required(request=req, verify_fresh=True, type="access")
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
