"""Focused tests for small edge branches in AuthX internals."""

from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from authx import AuthX, AuthXConfig
from authx._internal import _CallbackHandler, _ErrorHandler
from authx._internal._ratelimit import RateLimitBackend
from authx.exceptions import JWTDecodeError, RateLimitExceeded
from authx.main import TokenPayload
from authx.policy import PolicyContext, PolicyEvaluator, PolicyRule, _as_sequence, _read_value
from authx.schema import RequestToken
from authx.types import ModelCallback, RateLimitKeyFunc, SessionStoreProtocol, TokenCallback


def make_request(path: str = "/", method: str = "GET") -> Request:
    """Create a minimal HTTP request for direct dependency calls."""
    return Request(
        scope={
            "type": "http",
            "method": method,
            "path": path,
            "headers": [],
            "client": ("127.0.0.1", 1234),
        }
    )


@pytest.mark.asyncio
async def test_callback_model_check_true_with_none_callback_returns_none():
    handler = _CallbackHandler()
    handler.callback_get_model_instance = None

    with patch.object(handler, "_check_model_callback_is_set", return_value=True):
        assert await handler._get_current_subject("user") is None


@pytest.mark.asyncio
async def test_error_handler_rate_limit_direct_response():
    handler = _ErrorHandler()
    response = await handler._rate_limit_handler(
        request=make_request(),
        exc=RateLimitExceeded(retry_after=12),
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "12"
    assert response.body


def test_handle_errors_rate_limit_wrapper_response():
    app = FastAPI()
    AuthX().handle_errors(app)

    @app.get("/limited")
    def limited_route():
        raise RateLimitExceeded(retry_after=3)

    response = TestClient(app).get("/limited")

    assert response.status_code == 429
    assert response.json()["retry_after"] == 3


def test_login_type_mismatch_default_actual_unknown():
    from authx.exceptions import LoginTypeMismatchError

    exc = LoginTypeMismatchError(expected_type="admin")

    assert str(exc) == "Token type mismatch: expected 'admin', got 'unknown'"


def test_login_type_mismatch_custom_message_branch():
    from authx.exceptions import LoginTypeMismatchError

    exc = LoginTypeMismatchError(expected_type="admin", actual_type="user", message="custom mismatch")

    assert str(exc) == "custom mismatch"


@pytest.mark.asyncio
async def test_protocol_stub_methods_execute():
    assert TokenCallback.__call__(object(), "token") is None
    assert RateLimitKeyFunc.__call__(object(), make_request()) is None
    assert ModelCallback.__call__(object(), "uid") is None
    assert await RateLimitBackend.increment(object(), "key", 60) is None
    assert await RateLimitBackend.reset(object(), "key") is None
    assert await SessionStoreProtocol.create(object(), {"id": "session"}) is None
    assert await SessionStoreProtocol.get(object(), "session") is None
    assert await SessionStoreProtocol.update(object(), "session", active=True) is None
    assert await SessionStoreProtocol.delete(object(), "session") is None
    assert await SessionStoreProtocol.list_by_user(object(), "user") is None
    assert await SessionStoreProtocol.delete_all_by_user(object(), "user") is None


def test_previous_public_key_with_unsupported_algorithm_returns_none():
    config = AuthXConfig(JWT_SECRET_KEY="secret")
    config.JWT_ALGORITHM = "BLAH"  # type: ignore[assignment]

    assert config.previous_public_key is None


def test_decode_token_preserves_existing_exception_login_type():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"), login_type="admin")

    with patch.object(TokenPayload, "decode", side_effect=JWTDecodeError("bad", login_type="external")):
        with pytest.raises(JWTDecodeError) as exc_info:
            auth._decode_token("token")

    assert exc_info.value.login_type == "external"


def test_unset_access_cookies_without_csrf_cookie_branch():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    auth.config.JWT_COOKIE_CSRF_PROTECT = False
    response = JSONResponse(content={})

    auth.unset_access_cookies(response)

    assert len(response.headers.getlist("set-cookie")) == 1


def test_dependency_alias_properties_return_depends():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))

    assert auth.BUNDLE.dependency == auth.get_dependency
    assert auth.WS_AUTH_REQUIRED.dependency == auth._ws_auth_required


@pytest.mark.asyncio
async def test_auth_required_with_explicit_csrf_false_branch():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret", JWT_TOKEN_LOCATION=["headers"]))
    token = auth.create_access_token(uid="user")
    request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "headers": [[b"authorization", f"Bearer {token}".encode()]],
        }
    )

    payload = await auth._auth_required(request=request, verify_csrf=False)

    assert payload.sub == "user"


def test_verify_token_preserves_existing_exception_login_type():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"), login_type="admin")
    request_token = RequestToken(token="token", csrf=None, type="access", location="headers")

    with patch.object(RequestToken, "verify", side_effect=JWTDecodeError("bad", login_type="external")):
        with pytest.raises(JWTDecodeError) as exc_info:
            auth.verify_token(request_token)

    assert exc_info.value.login_type == "external"


@pytest.mark.asyncio
async def test_access_token_optional_dependency_closure_returns_token():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret", JWT_TOKEN_LOCATION=["headers"]))
    token = auth.create_access_token(uid="user")
    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "headers": [[b"authorization", f"Bearer {token}".encode()]],
        }
    )
    depends = auth.ACCESS_TOKEN

    request_token = await depends.dependency(request)  # type: ignore[union-attr]

    assert request_token is not None
    assert request_token.token == token


@pytest.mark.asyncio
async def test_websocket_missing_token_has_login_type():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"), login_type="admin")
    websocket = Mock()
    websocket.query_params = {}
    websocket.headers = {}

    with pytest.raises(Exception) as exc_info:
        await auth._ws_auth_required(websocket)

    assert exc_info.value.login_type == "admin"


def test_implicit_refresh_include_route_branch():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    auth.config.JWT_IMPLICIT_REFRESH_ROUTE_INCLUDE = ["/included"]
    request = make_request(path="/included")

    assert auth._implicit_refresh_enabled_for_request(request) is True


@pytest.mark.asyncio
async def test_implicit_refresh_middleware_refreshes_expiring_cookie_token():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret", JWT_TOKEN_LOCATION=["cookies"]))
    auth.config.JWT_COOKIE_CSRF_PROTECT = False
    auth.config.JWT_IMPLICIT_REFRESH_DELTATIME = timedelta(minutes=10)
    old_token = auth.create_access_token(uid="user", expiry=timedelta(seconds=1))
    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/refresh-me",
            "headers": [[b"cookie", f"{auth.config.JWT_ACCESS_COOKIE_NAME}={old_token};".encode()]],
        }
    )

    async def call_next(request: Request) -> JSONResponse:
        return JSONResponse(content={"ok": True})

    response = await auth.implicit_refresh_middleware(request, call_next)

    set_cookie_headers = response.headers.getlist("set-cookie")
    assert any(header.startswith(auth.config.JWT_ACCESS_COOKIE_NAME) for header in set_cookie_headers)


@pytest.mark.asyncio
async def test_implicit_refresh_middleware_skips_non_expiring_cookie_token():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret", JWT_TOKEN_LOCATION=["cookies"]))
    auth.config.JWT_COOKIE_CSRF_PROTECT = False
    auth.config.JWT_IMPLICIT_REFRESH_DELTATIME = timedelta(minutes=10)
    old_token = auth.create_access_token(uid="user", expiry=timedelta(hours=1))
    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/skip-refresh",
            "headers": [[b"cookie", f"{auth.config.JWT_ACCESS_COOKIE_NAME}={old_token};".encode()]],
        }
    )

    async def call_next(request: Request) -> JSONResponse:
        return JSONResponse(content={"ok": True})

    response = await auth.implicit_refresh_middleware(request, call_next)

    assert response.headers.getlist("set-cookie") == []


@pytest.mark.asyncio
async def test_rate_limited_dependency_runs_limiter_and_auth():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret", JWT_TOKEN_LOCATION=["headers"]))
    token = auth.create_access_token(uid="user")
    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "headers": [[b"authorization", f"Bearer {token}".encode()]],
            "client": ("127.0.0.1", 1234),
        }
    )
    dependency = auth.rate_limited(max_requests=1, window=60)

    payload = await dependency(request)

    assert payload.sub == "user"


@pytest.mark.asyncio
async def test_create_session_without_request_client_branch():
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    request = Mock()
    request.client = None
    request.headers = {"user-agent": "pytest"}

    session = await auth.create_session("user", request=request)

    assert session.uid == "user"
    assert session.ip_address is None
    assert session.user_agent == "pytest"


@pytest.mark.asyncio
async def test_session_store_update_ignores_unknown_and_filters_inactive():
    from authx._internal._session import InMemorySessionStore, SessionInfo

    store = InMemorySessionStore()
    active = SessionInfo(uid="user")
    inactive = SessionInfo(uid="user", is_active=False)
    await store.create(active)
    await store.create(inactive)

    await store.update(active.session_id, unknown="ignored", is_active=False)
    sessions = await store.list_by_user("user")

    assert sessions == []


def test_policy_helper_fallbacks_and_protocol_stub():
    context = PolicyContext(login_type="admin", action="read", resource="users")
    rule = PolicyRule(effect="allow", actions=["read"], resources=["users"])

    assert _read_value(None, "anything") is None
    assert _as_sequence("scope") == ["scope"]
    assert _as_sequence(123) == [123]
    assert PolicyEvaluator.__call__(object(), context, rule) is None
