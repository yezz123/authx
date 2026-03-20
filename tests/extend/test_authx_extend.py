from datetime import timedelta
from typing import Optional

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse

from authx import AuthX, AuthXConfig
from authx.exceptions import AuthXException


def _make_request(token: str) -> Request:
    return Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", f"Bearer {token}".encode())],
            "method": "GET",
            "path": "/",
            "scheme": "http",
            "server": ("testserver", 80),
        }
    )


@pytest.fixture(scope="function")
def authx():
    authx = AuthX()
    authx._config.JWT_SECRET_KEY = "SECRET"
    authx._config.JWT_TOKEN_LOCATION = ["headers", "json", "cookies"]

    return authx


@pytest.fixture(scope="function")
def mock_response():
    return JSONResponse(content={})


@pytest.mark.asyncio
async def test_auth_required_revoked_token(authx):
    token = authx.create_access_token(uid="test_user")

    async def is_token(t: str) -> bool:
        return t == token

    authx.is_token_in_blocklist = is_token

    with pytest.raises(AuthXException):
        await authx._auth_required(_make_request(token))


@pytest.mark.asyncio
async def test_get_current_subject(authx):
    token = authx.create_access_token(uid="test_user")

    async def get_user(uid: str) -> Optional[dict]:
        return {"id": uid, "username": f"user_{uid}"}

    authx.set_subject_getter(get_user)

    subject = await authx.get_current_subject(_make_request(token))
    assert subject == {"id": "test_user", "username": "user_test_user"}


@pytest.mark.asyncio
async def test_get_current_subject_sync_callback(authx):
    token = authx.create_access_token(uid="admin")

    def get_user_sync(uid: str) -> Optional[dict]:
        return {"id": uid, "role": "admin"}

    authx.set_subject_getter(get_user_sync)

    subject = await authx.get_current_subject(_make_request(token))
    assert subject == {"id": "admin", "role": "admin"}


@pytest.mark.asyncio
async def test_get_current_subject_no_callback_raises(authx):
    token = authx.create_access_token(uid="test_user")

    with pytest.raises(AttributeError, match="Model callback not set"):
        await authx.get_current_subject(_make_request(token))


@pytest.mark.asyncio
async def test_implicit_refresh_middleware(mock_response):
    config = AuthXConfig(
        JWT_SECRET_KEY="SECRET",
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_COOKIE_CSRF_PROTECT=False,
        JWT_IMPLICIT_REFRESH_DELTATIME=timedelta(minutes=5),
    )
    authx = AuthX(config=config)

    old_token = authx.create_access_token(uid="test_user", expiry=timedelta(seconds=30))

    cookie_header = f"{config.JWT_ACCESS_COOKIE_NAME}={old_token}".encode()
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"cookie", cookie_header)],
            "method": "GET",
            "path": "/dashboard",
            "query_string": b"",
            "root_path": "",
            "scheme": "http",
            "server": ("testserver", 80),
        }
    )

    async def mock_call_next(req):
        return mock_response

    response = await authx.implicit_refresh_middleware(request, mock_call_next)

    set_cookie_headers = [v for k, v in response.raw_headers if k.lower() == b"set-cookie"]
    assert len(set_cookie_headers) > 0
    cookie_value = set_cookie_headers[0].decode()
    assert config.JWT_ACCESS_COOKIE_NAME in cookie_value
    assert old_token not in cookie_value
