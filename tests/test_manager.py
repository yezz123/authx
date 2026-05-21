"""Tests for AuthManager."""

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from authx import AuthManager, AuthX, AuthXConfig
from authx.exceptions import BadConfigurationError, LoginTypeMismatchError, PolicyDeniedError
from authx.policy import PolicyRule
from authx.schema import RequestToken, TokenPayload


def make_auth(login_type: str, secret: str) -> AuthX:
    """Create a login-type aware AuthX instance."""
    return AuthX(
        config=AuthXConfig(
            JWT_SECRET_KEY=secret,
            JWT_TOKEN_LOCATION=["headers"],
        ),
        login_type=login_type,
    )


def test_register_requires_login_type():
    manager = AuthManager()
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))

    try:
        manager.register(auth)
    except BadConfigurationError as exc:
        assert "login_type" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected BadConfigurationError")


def test_register_rejects_duplicate_login_type():
    manager = AuthManager()
    manager.register(make_auth("admin", "admin-secret"))

    try:
        manager.register(make_auth("admin", "other-secret"))
    except BadConfigurationError as exc:
        assert "already registered" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected BadConfigurationError")


def test_create_access_token_uses_registered_context():
    manager = AuthManager()
    admin_auth = make_auth("admin", "admin-secret")
    user_auth = make_auth("user", "user-secret")
    manager.register(admin_auth)
    manager.register(user_auth)

    token = manager.create_access_token("admin", uid="root")
    payload = admin_auth._decode_token(token)

    assert payload.sub == "root"
    assert payload.login_type == "admin"


def test_create_token_pair_includes_login_type():
    manager = AuthManager()
    auth = make_auth("service", "service-secret")
    manager.register(auth)

    tokens = manager.create_token_pair("service", uid="svc")

    assert auth._decode_token(tokens.access_token).login_type == "service"
    assert auth._decode_token(tokens.refresh_token).login_type == "service"


def test_access_dependency_accepts_matching_login_type():
    manager = AuthManager()
    admin_auth = make_auth("admin", "admin-secret")
    manager.register(admin_auth)
    app = FastAPI()
    manager.handle_errors(app)

    @app.get("/admin", dependencies=[Depends(manager.access_token_required("admin"))])
    def admin_route():
        return {"ok": True}

    token = manager.create_access_token("admin", uid="root")
    response = TestClient(app).get("/admin", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_access_dependency_rejects_cross_type_token_with_mismatch_error():
    manager = AuthManager()
    manager.register(make_auth("admin", "admin-secret"))
    manager.register(make_auth("user", "user-secret"))
    app = FastAPI()
    manager.handle_errors(app)

    @app.get("/admin", dependencies=[Depends(manager.access_token_required("admin"))])
    def admin_route():
        return {"ok": True}

    token = manager.create_access_token("user", uid="alice")
    response = TestClient(app).get("/admin", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json() == {
        "message": "Token type mismatch: expected 'admin', got 'user'",
        "error_type": "LoginTypeMismatchError",
        "expected_type": "admin",
        "actual_type": "user",
    }


def test_login_types_and_unknown_login_type():
    manager = AuthManager()
    manager.register(make_auth("admin", "admin-secret"))
    manager.register(make_auth("user", "user-secret"))

    assert manager.login_types == ("admin", "user")
    with pytest.raises(BadConfigurationError, match="Unknown login_type"):
        manager.get("missing")


def test_create_refresh_token_uses_registered_context():
    manager = AuthManager()
    auth = make_auth("admin", "admin-secret")
    manager.register(auth)

    token = manager.create_refresh_token("admin", uid="root", scopes=["refresh"])
    payload = auth._decode_token(token)

    assert payload.sub == "root"
    assert payload.type == "refresh"
    assert payload.login_type == "admin"
    assert payload.scopes == ["refresh"]


def test_refresh_and_fresh_dependencies_accept_matching_tokens():
    manager = AuthManager()
    auth = make_auth("admin", "admin-secret")
    manager.register(auth)
    app = FastAPI()
    manager.handle_errors(app)

    @app.post("/refresh", dependencies=[Depends(manager.refresh_token_required("admin"))])
    def refresh_route():
        return {"ok": True}

    @app.post("/fresh", dependencies=[Depends(manager.fresh_token_required("admin"))])
    def fresh_route():
        return {"ok": True}

    client = TestClient(app)
    refresh_token = manager.create_refresh_token("admin", uid="root")
    fresh_token = manager.create_access_token("admin", uid="root", fresh=True)

    refresh_response = client.post("/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    fresh_response = client.post("/fresh", headers={"Authorization": f"Bearer {fresh_token}"})

    assert refresh_response.status_code == 200
    assert fresh_response.status_code == 200


def test_token_required_custom_locations_accepts_query_token():
    manager = AuthManager()
    auth = make_auth("admin", "admin-secret")
    auth.config.JWT_TOKEN_LOCATION = ["query"]
    manager.register(auth)
    app = FastAPI()
    manager.handle_errors(app)

    @app.get("/query", dependencies=[Depends(manager.token_required("admin", locations=["query"]))])
    def query_route():
        return {"ok": True}

    token = manager.create_access_token("admin", uid="root")
    response = TestClient(app).get(f"/query?token={token}")

    assert response.status_code == 200


def test_access_dependency_reraises_jwt_decode_error_when_no_registered_type_matches():
    manager = AuthManager()
    manager.register(make_auth("admin", "admin-secret"))
    manager.register(make_auth("user", "user-secret"))
    app = FastAPI()
    manager.handle_errors(app)

    @app.get("/admin", dependencies=[Depends(manager.access_token_required("admin"))])
    def admin_route():
        return {"ok": True}

    token = AuthX(config=AuthXConfig(JWT_SECRET_KEY="external-secret")).create_access_token(uid="outsider")
    response = TestClient(app).get("/admin", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 422
    assert response.json()["error_type"] == "TokenInvalidSignatureError"


def test_verify_login_type_rejects_missing_login_type():
    manager = AuthManager()
    manager.register(make_auth("admin", "admin-secret"))

    with pytest.raises(LoginTypeMismatchError) as exc_info:
        manager._verify_login_type(TokenPayload(sub="root"), "admin")

    assert exc_info.value.expected_type == "admin"
    assert exc_info.value.actual_type is None


def test_payload_login_type_returns_none_for_missing_claim():
    manager = AuthManager()
    payload = TokenPayload(sub="root")

    assert manager._payload_login_type(payload) is None


def test_try_verify_with_auth_returns_none_for_bad_token():
    manager = AuthManager()
    auth = make_auth("admin", "admin-secret")
    request_token = RequestToken(token="bad.token.value", csrf=None, type="access", location="headers")

    assert manager._try_verify_with_auth(auth, request_token) is None


@pytest.mark.asyncio
async def test_authorize_without_request_or_payload_denies():
    manager = AuthManager()

    with pytest.raises(PolicyDeniedError, match="request or token payload"):
        await manager.authorize("admin", "users:read", "users")


@pytest.mark.asyncio
async def test_authorize_with_payload_and_matching_policy_returns_payload():
    manager = AuthManager(policy_rules=[PolicyRule(effect="allow", actions=["users:read"], resources=["users"])])
    manager.register(make_auth("admin", "admin-secret"))
    payload = TokenPayload(sub="root", login_type="admin")

    result = await manager.authorize("admin", "users:read", "users", payload=payload)

    assert result is payload


@pytest.mark.asyncio
async def test_authorize_with_payload_mismatched_login_type_raises():
    manager = AuthManager()
    manager.register(make_auth("admin", "admin-secret"))
    payload = TokenPayload(sub="root", login_type="user")

    with pytest.raises(LoginTypeMismatchError):
        await manager.authorize("admin", "users:read", "users", payload=payload)


def test_add_policy_rule_and_evaluator_delegate_to_policy_engine():
    manager = AuthManager()
    rule = PolicyRule(effect="allow", actions=["*"], resources=["*"])

    def evaluator(context, policy_rule):
        return True

    manager.add_policy_rule(rule)
    manager.add_policy_evaluator(evaluator)

    assert manager.policy_engine.rules == [rule]
