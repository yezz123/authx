"""Tests for AuthManager."""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from authx import AuthManager, AuthX, AuthXConfig
from authx.exceptions import BadConfigurationError


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
