"""Tests for scope management functionality."""

from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from authx import AuthX, AuthXConfig, InsufficientScopeError
from authx.schema import TokenPayload


@pytest.fixture
def config():
    """Fixture for AuthX Configuration."""
    return AuthXConfig(
        JWT_SECRET_KEY="test-secret-key",
        JWT_TOKEN_LOCATION=["headers"],
    )


@pytest.fixture
def auth(config: AuthXConfig):
    """Fixture for AuthX instance."""
    return AuthX(config=config)


@pytest.fixture
def app(auth: AuthX):
    """Fixture for FastAPI app with scope-protected routes."""
    app = FastAPI()
    auth.handle_errors(app)

    # Route with single scope requirement
    @app.get("/read", dependencies=[Depends(auth.scopes_required("read"))])
    async def read_route():
        return {"message": "read access granted"}

    # Route with multiple scopes (AND)
    @app.get(
        "/read-write",
        dependencies=[Depends(auth.scopes_required("read", "write"))],
    )
    async def read_write_route():
        return {"message": "read-write access granted"}

    # Route with multiple scopes (OR)
    @app.get(
        "/admin-or-moderator",
        dependencies=[Depends(auth.scopes_required("admin", "moderator", all_required=False))],
    )
    async def admin_or_moderator_route():
        return {"message": "admin or moderator access granted"}

    # Route with hierarchical scope
    @app.get(
        "/users-read",
        dependencies=[Depends(auth.scopes_required("users:read"))],
    )
    async def users_read_route():
        return {"message": "users:read access granted"}

    # Route with wildcard-satisfiable scope
    @app.get(
        "/admin-users",
        dependencies=[Depends(auth.scopes_required("admin:users"))],
    )
    async def admin_users_route():
        return {"message": "admin:users access granted"}

    # Route that returns payload - using Annotated to avoid B008
    ProfilePayload = Annotated[TokenPayload, Depends(auth.scopes_required("profile:read"))]

    @app.get("/profile")
    async def profile_route(
        payload: ProfilePayload,
    ):
        return {"user": payload.sub, "scopes": payload.scopes}

    return app


@pytest.fixture
def client(app: FastAPI):
    """Fixture for TestClient."""
    return TestClient(app)


class TestTokenCreationWithScopes:
    """Tests for creating tokens with scopes."""

    def test_create_access_token_with_scopes(self, auth: AuthX):
        """Test creating access token with scopes."""
        token = auth.create_access_token(uid="user1", scopes=["read", "write"])
        payload = auth._decode_token(token)

        assert payload.scopes == ["read", "write"]
        assert payload.sub == "user1"

    def test_create_access_token_without_scopes(self, auth: AuthX):
        """Test creating access token without scopes."""
        token = auth.create_access_token(uid="user1")
        payload = auth._decode_token(token)

        assert payload.scopes is None
        assert payload.sub == "user1"

    def test_create_access_token_with_empty_scopes(self, auth: AuthX):
        """Test creating access token with empty scopes list."""
        token = auth.create_access_token(uid="user1", scopes=[])
        payload = auth._decode_token(token)

        assert payload.scopes == []

    def test_create_refresh_token_with_scopes(self, auth: AuthX):
        """Test creating refresh token with scopes."""
        token = auth.create_refresh_token(uid="user1", scopes=["refresh"])
        payload = auth._decode_token(token)

        assert payload.scopes == ["refresh"]

    def test_create_token_with_hierarchical_scopes(self, auth: AuthX):
        """Test creating token with hierarchical scopes."""
        token = auth.create_access_token(
            uid="user1",
            scopes=["users:read", "users:write", "posts:read"],
        )
        payload = auth._decode_token(token)

        assert "users:read" in payload.scopes
        assert "users:write" in payload.scopes
        assert "posts:read" in payload.scopes

    def test_create_token_with_wildcard_scope(self, auth: AuthX):
        """Test creating token with wildcard scope."""
        token = auth.create_access_token(uid="admin", scopes=["admin:*"])
        payload = auth._decode_token(token)

        assert payload.scopes == ["admin:*"]


class TestScopesRequiredDependency:
    """Tests for scopes_required dependency."""

    def test_single_scope_access_granted(self, client: TestClient, auth: AuthX):
        """Test access granted with matching single scope."""
        token = auth.create_access_token(uid="user1", scopes=["read"])

        response = client.get("/read", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()["message"] == "read access granted"

    def test_single_scope_access_denied(self, client: TestClient, auth: AuthX):
        """Test access denied without matching scope."""
        token = auth.create_access_token(uid="user1", scopes=["write"])

        response = client.get("/read", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403

    def test_multiple_scopes_and_logic_granted(self, client: TestClient, auth: AuthX):
        """Test access granted with all required scopes (AND logic)."""
        token = auth.create_access_token(uid="user1", scopes=["read", "write"])

        response = client.get("/read-write", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200

    def test_multiple_scopes_and_logic_denied(self, client: TestClient, auth: AuthX):
        """Test access denied with partial scopes (AND logic)."""
        token = auth.create_access_token(uid="user1", scopes=["read"])

        response = client.get("/read-write", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403

    def test_multiple_scopes_or_logic_granted_first(self, client: TestClient, auth: AuthX):
        """Test access granted with first scope (OR logic)."""
        token = auth.create_access_token(uid="user1", scopes=["admin"])

        response = client.get(
            "/admin-or-moderator",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_multiple_scopes_or_logic_granted_second(self, client: TestClient, auth: AuthX):
        """Test access granted with second scope (OR logic)."""
        token = auth.create_access_token(uid="user1", scopes=["moderator"])

        response = client.get(
            "/admin-or-moderator",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_multiple_scopes_or_logic_denied(self, client: TestClient, auth: AuthX):
        """Test access denied without any required scope (OR logic)."""
        token = auth.create_access_token(uid="user1", scopes=["user"])

        response = client.get(
            "/admin-or-moderator",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_hierarchical_scope_exact_match(self, client: TestClient, auth: AuthX):
        """Test access granted with exact hierarchical scope match."""
        token = auth.create_access_token(uid="user1", scopes=["users:read"])

        response = client.get("/users-read", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200

    def test_wildcard_scope_grants_access(self, client: TestClient, auth: AuthX):
        """Test wildcard scope grants access to specific scope requirement."""
        token = auth.create_access_token(uid="admin", scopes=["admin:*"])

        response = client.get("/admin-users", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()["message"] == "admin:users access granted"

    def test_wildcard_scope_wrong_namespace(self, client: TestClient, auth: AuthX):
        """Test wildcard scope doesn't grant access to different namespace."""
        token = auth.create_access_token(uid="user1", scopes=["users:*"])

        response = client.get("/admin-users", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403

    def test_no_scopes_in_token(self, client: TestClient, auth: AuthX):
        """Test access denied when token has no scopes."""
        token = auth.create_access_token(uid="user1")

        response = client.get("/read", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 403

    def test_payload_returned(self, client: TestClient, auth: AuthX):
        """Test payload is returned from scopes_required dependency."""
        token = auth.create_access_token(
            uid="user123",
            scopes=["profile:read", "profile:write"],
        )

        response = client.get("/profile", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["user"] == "user123"
        assert "profile:read" in data["scopes"]


class TestTokenPayloadHasScopes:
    """Tests for TokenPayload.has_scopes method."""

    def test_has_scopes_simple_match(self):
        """Test simple scope matching."""
        payload = TokenPayload(sub="user1", scopes=["read", "write"])

        assert payload.has_scopes("read") is True
        assert payload.has_scopes("write") is True
        assert payload.has_scopes("admin") is False

    def test_has_scopes_multiple_all_required(self):
        """Test multiple scopes with AND logic."""
        payload = TokenPayload(sub="user1", scopes=["read", "write", "delete"])

        assert payload.has_scopes("read", "write") is True
        assert payload.has_scopes("read", "write", "delete") is True
        assert payload.has_scopes("read", "admin") is False

    def test_has_scopes_multiple_any_required(self):
        """Test multiple scopes with OR logic."""
        payload = TokenPayload(sub="user1", scopes=["read"])

        assert payload.has_scopes("read", "admin", all_required=False) is True
        assert payload.has_scopes("admin", "superuser", all_required=False) is False

    def test_has_scopes_wildcard_match(self):
        """Test wildcard scope matching."""
        payload = TokenPayload(sub="admin", scopes=["admin:*"])

        assert payload.has_scopes("admin:users") is True
        assert payload.has_scopes("admin:settings") is True
        assert payload.has_scopes("admin") is True
        assert payload.has_scopes("users:read") is False

    def test_has_scopes_none(self):
        """Test with None scopes."""
        payload = TokenPayload(sub="user1", scopes=None)

        assert payload.has_scopes("read") is False
        assert payload.has_scopes("read", all_required=False) is False

    def test_has_scopes_empty(self):
        """Test with empty scopes list."""
        payload = TokenPayload(sub="user1", scopes=[])

        assert payload.has_scopes("read") is False


class TestInsufficientScopeError:
    """Tests for InsufficientScopeError exception."""

    def test_exception_attributes(self):
        """Test exception stores required and provided scopes."""
        exc = InsufficientScopeError(
            required=["admin", "superuser"],
            provided=["read", "write"],
        )

        assert exc.required == ["admin", "superuser"]
        assert exc.provided == ["read", "write"]

    def test_exception_message(self):
        """Test exception message format."""
        exc = InsufficientScopeError(
            required=["admin"],
            provided=["read"],
        )

        assert "admin" in str(exc)
        assert "read" in str(exc)

    def test_exception_none_provided(self):
        """Test exception with None provided scopes."""
        exc = InsufficientScopeError(required=["admin"], provided=None)

        assert exc.provided == []

    def test_exception_custom_message(self):
        """Test exception with custom message."""
        exc = InsufficientScopeError(
            required=["admin"],
            message="Custom error message",
        )

        assert str(exc) == "Custom error message"


class TestScopesWithOtherFeatures:
    """Tests for scopes combined with other AuthX features."""

    def test_scopes_with_fresh_token(self, auth: AuthX):
        """Test scopes work with fresh tokens."""
        token = auth.create_access_token(
            uid="user1",
            fresh=True,
            scopes=["admin"],
        )
        payload = auth._decode_token(token)

        assert payload.fresh is True
        assert payload.scopes == ["admin"]

    def test_scopes_with_additional_data(self, auth: AuthX):
        """Test scopes work with additional token data."""
        token = auth.create_access_token(
            uid="user1",
            scopes=["read"],
            data={"role": "editor"},
        )
        payload = auth._decode_token(token)

        assert payload.scopes == ["read"]
        # Additional data should be accessible
        assert hasattr(payload, "role") or "role" in payload.extra_dict or payload.model_dump().get("role") == "editor"

    def test_scopes_preserved_in_encode_decode(self, auth: AuthX):
        """Test scopes are preserved through encode/decode cycle."""
        original_scopes = ["users:read", "users:write", "admin:*"]
        token = auth.create_access_token(uid="user1", scopes=original_scopes)
        payload = auth._decode_token(token)

        assert payload.scopes == original_scopes
