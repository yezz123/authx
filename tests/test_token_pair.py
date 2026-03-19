"""Tests for TokenResponse schema and create_token_pair helper."""

from datetime import timedelta
from unittest.mock import Mock

from fastapi import Response

from authx import AuthX, AuthXConfig, AuthXDependency, TokenResponse


class TestTokenResponseSchema:
    """Tests for the TokenResponse Pydantic model."""

    def test_basic_construction(self):
        resp = TokenResponse(access_token="acc", refresh_token="ref")
        assert resp.access_token == "acc"
        assert resp.refresh_token == "ref"
        assert resp.token_type == "bearer"

    def test_custom_token_type(self):
        resp = TokenResponse(access_token="a", refresh_token="r", token_type="mac")
        assert resp.token_type == "mac"

    def test_serialization(self):
        resp = TokenResponse(access_token="acc", refresh_token="ref")
        data = resp.model_dump()
        assert data == {
            "access_token": "acc",
            "refresh_token": "ref",
            "token_type": "bearer",
        }

    def test_json_serialization(self):
        resp = TokenResponse(access_token="acc", refresh_token="ref")
        json_str = resp.model_dump_json()
        assert '"access_token":"acc"' in json_str
        assert '"refresh_token":"ref"' in json_str
        assert '"token_type":"bearer"' in json_str


class TestCreateTokenPair:
    """Tests for AuthX.create_token_pair."""

    def _make_auth(self) -> AuthX:
        return AuthX(config=AuthXConfig(JWT_SECRET_KEY="test-secret"))

    def test_returns_token_response(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1")
        assert isinstance(result, TokenResponse)
        assert result.token_type == "bearer"

    def test_tokens_are_valid_jwts(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1")

        access_payload = auth._decode_token(result.access_token)
        refresh_payload = auth._decode_token(result.refresh_token)

        assert access_payload.sub == "user1"
        assert access_payload.type == "access"
        assert refresh_payload.sub == "user1"
        assert refresh_payload.type == "refresh"

    def test_access_and_refresh_are_different(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1")
        assert result.access_token != result.refresh_token

    def test_fresh_flag(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1", fresh=True)

        access_payload = auth._decode_token(result.access_token)
        assert access_payload.fresh is True

    def test_custom_access_expiry(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1", access_expiry=timedelta(hours=2))

        payload = auth._decode_token(result.access_token)
        assert payload.time_until_expiry.total_seconds() > 7100

    def test_custom_refresh_expiry(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1", refresh_expiry=timedelta(days=7))

        payload = auth._decode_token(result.refresh_token)
        seconds_in_7_days = 7 * 24 * 3600
        assert payload.time_until_expiry.total_seconds() > seconds_in_7_days - 60

    def test_access_scopes(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1", access_scopes=["read", "write"])

        payload = auth._decode_token(result.access_token)
        assert payload.has_scopes("read", "write")

    def test_refresh_scopes(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1", refresh_scopes=["refresh"])

        payload = auth._decode_token(result.refresh_token)
        assert payload.has_scopes("refresh")

    def test_separate_access_and_refresh_scopes(self):
        auth = self._make_auth()
        result = auth.create_token_pair(
            uid="user1",
            access_scopes=["users:read"],
            refresh_scopes=["refresh:token"],
        )

        access_payload = auth._decode_token(result.access_token)
        refresh_payload = auth._decode_token(result.refresh_token)

        assert access_payload.has_scopes("users:read")
        assert not access_payload.has_scopes("refresh:token")
        assert refresh_payload.has_scopes("refresh:token")

    def test_additional_data(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1", data={"role": "admin"})

        access_dumped = auth._decode_token(result.access_token).model_dump()
        refresh_dumped = auth._decode_token(result.refresh_token).model_dump()

        assert access_dumped["role"] == "admin"
        assert refresh_dumped["role"] == "admin"

    def test_audience_claim(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1", audience="myapp")

        access_payload = auth._decode_token(result.access_token, audience="myapp")
        assert access_payload.aud == "myapp"

    def test_model_dump_for_api_response(self):
        auth = self._make_auth()
        result = auth.create_token_pair(uid="user1")
        data = result.model_dump()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


class TestCreateTokenPairDependency:
    """Tests for AuthXDependency.create_token_pair delegation."""

    def test_delegates_to_authx(self):
        expected = TokenResponse(access_token="a", refresh_token="r")
        mock_authx = Mock()
        mock_authx.create_token_pair.return_value = expected

        request = Mock(scope={"type": "http"})
        response = Mock(spec=Response)
        dep = AuthXDependency(mock_authx, request, response)

        result = dep.create_token_pair(uid="user1", fresh=True)

        assert result is expected
        mock_authx.create_token_pair.assert_called_once_with(
            uid="user1",
            fresh=True,
            headers=None,
            access_expiry=None,
            refresh_expiry=None,
            data=None,
            audience=None,
            access_scopes=None,
            refresh_scopes=None,
        )

    def test_passes_all_params(self):
        mock_authx = Mock()
        mock_authx.create_token_pair.return_value = TokenResponse(access_token="a", refresh_token="r")

        request = Mock(scope={"type": "http"})
        response = Mock(spec=Response)
        dep = AuthXDependency(mock_authx, request, response)

        dep.create_token_pair(
            uid="u",
            fresh=True,
            access_expiry=timedelta(hours=1),
            refresh_expiry=timedelta(days=7),
            data={"role": "admin"},
            audience="app",
            access_scopes=["read"],
            refresh_scopes=["refresh"],
        )

        mock_authx.create_token_pair.assert_called_once_with(
            uid="u",
            fresh=True,
            headers=None,
            access_expiry=timedelta(hours=1),
            refresh_expiry=timedelta(days=7),
            data={"role": "admin"},
            audience="app",
            access_scopes=["read"],
            refresh_scopes=["refresh"],
        )
