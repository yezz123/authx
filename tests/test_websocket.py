"""Tests for WebSocket authentication support."""

from typing import Any

import pytest
from fastapi import WebSocket

from authx import AuthX, AuthXConfig
from authx.exceptions import JWTDecodeError, MissingTokenError, RevokedTokenError


async def _noop_receive() -> dict[str, Any]:
    raise NotImplementedError


async def _noop_send(msg: dict[str, Any]) -> None:
    raise NotImplementedError


@pytest.fixture
def auth():
    return AuthX(config=AuthXConfig(JWT_SECRET_KEY="ws-secret"))


def _ws(query_string: bytes = b"", headers: list[tuple[bytes, bytes]] | None = None) -> WebSocket:
    return WebSocket(
        scope={
            "type": "websocket",
            "headers": headers or [],
            "query_string": query_string,
            "path": "/ws",
            "scheme": "ws",
            "server": ("testserver", 80),
        },
        receive=_noop_receive,
        send=_noop_send,
    )


class TestWebSocketAuthRequired:
    """Tests for _ws_auth_required."""

    @pytest.mark.asyncio
    async def test_token_from_query_param(self, auth):
        token = auth.create_access_token(uid="user1")
        ws = _ws(query_string=f"token={token}".encode())

        payload = await auth._ws_auth_required(ws)
        assert payload.sub == "user1"
        assert payload.type == "access"

    @pytest.mark.asyncio
    async def test_token_from_authorization_header(self, auth):
        token = auth.create_access_token(uid="user2")
        ws = _ws(headers=[(b"authorization", f"Bearer {token}".encode())])

        payload = await auth._ws_auth_required(ws)
        assert payload.sub == "user2"

    @pytest.mark.asyncio
    async def test_token_from_header_without_bearer_prefix(self):
        auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="ws-secret", JWT_HEADER_TYPE=""))
        token = auth.create_access_token(uid="user3")
        ws = _ws(headers=[(b"authorization", token.encode())])

        payload = await auth._ws_auth_required(ws)
        assert payload.sub == "user3"

    @pytest.mark.asyncio
    async def test_query_param_takes_precedence(self, auth):
        token_q = auth.create_access_token(uid="query-user")
        token_h = auth.create_access_token(uid="header-user")
        ws = _ws(
            query_string=f"token={token_q}".encode(),
            headers=[(b"authorization", f"Bearer {token_h}".encode())],
        )

        payload = await auth._ws_auth_required(ws)
        assert payload.sub == "query-user"

    @pytest.mark.asyncio
    async def test_missing_token_raises(self, auth):
        ws = _ws()
        with pytest.raises(MissingTokenError, match="Missing token in WebSocket"):
            await auth._ws_auth_required(ws)

    @pytest.mark.asyncio
    async def test_invalid_token_raises(self, auth):
        ws = _ws(query_string=b"token=invalid.jwt.token")
        with pytest.raises(JWTDecodeError):
            await auth._ws_auth_required(ws)

    @pytest.mark.asyncio
    async def test_wrong_key_raises(self):
        auth1 = AuthX(config=AuthXConfig(JWT_SECRET_KEY="key-one"))
        auth2 = AuthX(config=AuthXConfig(JWT_SECRET_KEY="key-two"))
        token = auth1.create_access_token(uid="user1")
        ws = _ws(query_string=f"token={token}".encode())

        with pytest.raises(JWTDecodeError):
            await auth2._ws_auth_required(ws)

    @pytest.mark.asyncio
    async def test_revoked_token_raises(self, auth):
        token = auth.create_access_token(uid="user1")
        auth.set_token_blocklist(lambda t: t == token)
        ws = _ws(query_string=f"token={token}".encode())

        with pytest.raises(RevokedTokenError):
            await auth._ws_auth_required(ws)

    @pytest.mark.asyncio
    async def test_custom_query_param_name(self):
        auth = AuthX(
            config=AuthXConfig(
                JWT_SECRET_KEY="ws-secret",
                JWT_QUERY_STRING_NAME="jwt",
            )
        )
        token = auth.create_access_token(uid="custom")
        ws = _ws(query_string=f"jwt={token}".encode())

        payload = await auth._ws_auth_required(ws)
        assert payload.sub == "custom"

    @pytest.mark.asyncio
    async def test_token_with_scopes(self, auth):
        token = auth.create_access_token(uid="scoped", scopes=["chat:read", "chat:write"])
        ws = _ws(query_string=f"token={token}".encode())

        payload = await auth._ws_auth_required(ws)
        assert payload.has_scopes("chat:read", "chat:write")

    @pytest.mark.asyncio
    async def test_expired_token_raises(self, auth):
        from datetime import timedelta

        token = auth.create_access_token(uid="user1", expiry=timedelta(seconds=-1))
        ws = _ws(query_string=f"token={token}".encode())

        with pytest.raises(JWTDecodeError):
            await auth._ws_auth_required(ws)
