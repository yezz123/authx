"""Tests for JWT signing key rotation support."""

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Request
from starlette.datastructures import Headers, MutableHeaders

from authx import AuthX, AuthXConfig
from authx.exceptions import JWTDecodeError


def _rsa_keypair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


class TestSymmetricKeyRotation:
    """Key rotation with HS256."""

    def test_token_signed_with_current_key(self):
        auth = AuthX(
            config=AuthXConfig(
                JWT_SECRET_KEY="new-secret",
                JWT_PREVIOUS_SECRET_KEY="old-secret",
            )
        )
        token = auth.create_access_token(uid="user1")
        payload = auth._decode_token(token)
        assert payload.sub == "user1"

    def test_token_signed_with_previous_key(self):
        old_auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="old-secret"))
        token = old_auth.create_access_token(uid="user1")

        new_auth = AuthX(
            config=AuthXConfig(
                JWT_SECRET_KEY="new-secret",
                JWT_PREVIOUS_SECRET_KEY="old-secret",
            )
        )
        payload = new_auth._decode_token(token)
        assert payload.sub == "user1"

    def test_token_signed_with_unknown_key_fails(self):
        unknown_auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="unknown-secret"))
        token = unknown_auth.create_access_token(uid="user1")

        new_auth = AuthX(
            config=AuthXConfig(
                JWT_SECRET_KEY="new-secret",
                JWT_PREVIOUS_SECRET_KEY="old-secret",
            )
        )
        with pytest.raises(JWTDecodeError):
            new_auth._decode_token(token)

    def test_no_previous_key_does_not_fallback(self):
        old_auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="old-secret"))
        token = old_auth.create_access_token(uid="user1")

        new_auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="new-secret"))
        with pytest.raises(JWTDecodeError):
            new_auth._decode_token(token)

    def test_new_tokens_always_use_current_key(self):
        auth = AuthX(
            config=AuthXConfig(
                JWT_SECRET_KEY="new-secret",
                JWT_PREVIOUS_SECRET_KEY="old-secret",
            )
        )
        token = auth.create_access_token(uid="user1")

        current_only = AuthX(config=AuthXConfig(JWT_SECRET_KEY="new-secret"))
        payload = current_only._decode_token(token)
        assert payload.sub == "user1"

    @pytest.mark.asyncio
    async def test_verify_token_falls_back_to_previous_key(self):
        old_auth = AuthX(
            config=AuthXConfig(
                JWT_SECRET_KEY="old-secret",
                JWT_TOKEN_LOCATION=["headers"],
            )
        )
        token = old_auth.create_access_token(uid="user1")

        new_auth = AuthX(
            config=AuthXConfig(
                JWT_SECRET_KEY="new-secret",
                JWT_PREVIOUS_SECRET_KEY="old-secret",
                JWT_TOKEN_LOCATION=["headers"],
            )
        )

        request = Request(
            scope={
                "type": "http",
                "headers": [],
                "method": "GET",
                "path": "/",
                "scheme": "http",
                "server": ("testserver", 80),
            }
        )
        request._headers = MutableHeaders(headers=Headers(raw=[]))
        request._headers["Authorization"] = f"Bearer {token}"

        payload = await new_auth._auth_required(request)
        assert payload.sub == "user1"


class TestAsymmetricKeyRotation:
    """Key rotation with RS256."""

    def test_token_signed_with_previous_rsa_key(self):
        old_priv, old_pub = _rsa_keypair()
        new_priv, new_pub = _rsa_keypair()

        old_auth = AuthX(
            config=AuthXConfig(
                JWT_ALGORITHM="RS256",
                JWT_PRIVATE_KEY=old_priv,
                JWT_PUBLIC_KEY=old_pub,
            )
        )
        token = old_auth.create_access_token(uid="alice")

        new_auth = AuthX(
            config=AuthXConfig(
                JWT_ALGORITHM="RS256",
                JWT_PRIVATE_KEY=new_priv,
                JWT_PUBLIC_KEY=new_pub,
                JWT_PREVIOUS_PUBLIC_KEY=old_pub,
            )
        )
        payload = new_auth._decode_token(token)
        assert payload.sub == "alice"

    def test_rsa_no_previous_key_fails(self):
        old_priv, old_pub = _rsa_keypair()
        new_priv, new_pub = _rsa_keypair()

        old_auth = AuthX(
            config=AuthXConfig(
                JWT_ALGORITHM="RS256",
                JWT_PRIVATE_KEY=old_priv,
                JWT_PUBLIC_KEY=old_pub,
            )
        )
        token = old_auth.create_access_token(uid="alice")

        new_auth = AuthX(
            config=AuthXConfig(
                JWT_ALGORITHM="RS256",
                JWT_PRIVATE_KEY=new_priv,
                JWT_PUBLIC_KEY=new_pub,
            )
        )
        with pytest.raises(JWTDecodeError):
            new_auth._decode_token(token)


class TestConfigPreviousKey:
    """Config property tests for previous_public_key."""

    def test_symmetric_returns_previous_secret(self):
        config = AuthXConfig(
            JWT_SECRET_KEY="current",
            JWT_PREVIOUS_SECRET_KEY="old",
        )
        assert config.previous_public_key == "old"

    def test_symmetric_returns_none_when_not_set(self):
        config = AuthXConfig(JWT_SECRET_KEY="current")
        assert config.previous_public_key is None

    def test_asymmetric_returns_previous_public(self):
        _, pub = _rsa_keypair()
        config = AuthXConfig(
            JWT_ALGORITHM="RS256",
            JWT_PRIVATE_KEY="dummy",
            JWT_PUBLIC_KEY="dummy",
            JWT_PREVIOUS_PUBLIC_KEY=pub,
        )
        assert config.previous_public_key == pub

    def test_asymmetric_returns_none_when_not_set(self):
        config = AuthXConfig(
            JWT_ALGORITHM="RS256",
            JWT_PRIVATE_KEY="dummy",
            JWT_PUBLIC_KEY="dummy",
        )
        assert config.previous_public_key is None
