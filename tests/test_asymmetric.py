"""End-to-end tests for asymmetric JWT algorithms (RS256, ES256)."""

from datetime import timedelta

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from authx import AuthX, AuthXConfig
from authx.exceptions import JWTDecodeError
from authx.token import create_token, decode_token
from tests.utils import generate_ec_keypair as _ec_keypair
from tests.utils import generate_rsa_keypair as _rsa_keypair


class TestLowLevelAsymmetric:
    """Low-level create_token / decode_token with asymmetric keys."""

    @pytest.mark.parametrize("algorithm", ["RS256", "RS384", "RS512"])
    def test_rsa_round_trip(self, algorithm):
        private_pem, public_pem = _rsa_keypair()
        token = create_token(uid="user1", key=private_pem, algorithm=algorithm, type="access")
        payload = decode_token(token, key=public_pem, algorithms=[algorithm])
        assert payload["sub"] == "user1"
        assert payload["type"] == "access"

    @pytest.mark.parametrize("algorithm", ["ES256", "ES384"])
    def test_ec_round_trip(self, algorithm):
        curve = ec.SECP256R1() if algorithm == "ES256" else ec.SECP384R1()
        private_key = ec.generate_private_key(curve)
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

        token = create_token(uid="user2", key=private_pem, algorithm=algorithm, type="refresh")
        payload = decode_token(token, key=public_pem, algorithms=[algorithm])
        assert payload["sub"] == "user2"
        assert payload["type"] == "refresh"

    def test_rsa_wrong_public_key_fails(self):
        private_pem, _ = _rsa_keypair()
        _, wrong_public = _rsa_keypair()
        token = create_token(uid="user1", key=private_pem, algorithm="RS256", type="access")
        with pytest.raises(JWTDecodeError):
            decode_token(token, key=wrong_public, algorithms=["RS256"])

    def test_ec_wrong_public_key_fails(self):
        private_pem, _ = _ec_keypair()
        _, wrong_public = _ec_keypair()
        token = create_token(uid="user1", key=private_pem, algorithm="ES256", type="access")
        with pytest.raises(JWTDecodeError):
            decode_token(token, key=wrong_public, algorithms=["ES256"])

    def test_algorithm_mismatch_fails(self):
        private_pem, public_pem = _rsa_keypair()
        token = create_token(uid="user1", key=private_pem, algorithm="RS256", type="access")
        with pytest.raises(JWTDecodeError):
            decode_token(token, key=public_pem, algorithms=["ES256"])


class TestAuthXAsymmetric:
    """Full AuthX class E2E with asymmetric algorithms."""

    @pytest.mark.parametrize("algorithm", ["RS256", "ES256"])
    def test_create_and_decode_access_token(self, algorithm):
        if algorithm.startswith("RS"):
            private_pem, public_pem = _rsa_keypair()
        else:
            private_pem, public_pem = _ec_keypair()

        config = AuthXConfig(
            JWT_ALGORITHM=algorithm,
            JWT_PRIVATE_KEY=private_pem,
            JWT_PUBLIC_KEY=public_pem,
        )
        auth = AuthX(config=config)

        token = auth.create_access_token(uid="alice", fresh=True)
        payload = auth._decode_token(token)
        assert payload.sub == "alice"
        assert payload.type == "access"
        assert payload.fresh is True

    @pytest.mark.parametrize("algorithm", ["RS256", "ES256"])
    def test_create_and_decode_refresh_token(self, algorithm):
        if algorithm.startswith("RS"):
            private_pem, public_pem = _rsa_keypair()
        else:
            private_pem, public_pem = _ec_keypair()

        config = AuthXConfig(
            JWT_ALGORITHM=algorithm,
            JWT_PRIVATE_KEY=private_pem,
            JWT_PUBLIC_KEY=public_pem,
        )
        auth = AuthX(config=config)

        token = auth.create_refresh_token(uid="bob")
        payload = auth._decode_token(token)
        assert payload.sub == "bob"
        assert payload.type == "refresh"

    def test_rs256_with_scopes(self):
        private_pem, public_pem = _rsa_keypair()
        config = AuthXConfig(
            JWT_ALGORITHM="RS256",
            JWT_PRIVATE_KEY=private_pem,
            JWT_PUBLIC_KEY=public_pem,
        )
        auth = AuthX(config=config)

        token = auth.create_access_token(uid="admin", scopes=["users:read", "users:write"])
        payload = auth._decode_token(token)
        assert payload.sub == "admin"
        assert payload.has_scopes("users:read")
        assert payload.has_scopes("users:read", "users:write")
        assert not payload.has_scopes("admin:delete")

    def test_es256_with_custom_expiry(self):
        private_pem, public_pem = _ec_keypair()
        config = AuthXConfig(
            JWT_ALGORITHM="ES256",
            JWT_PRIVATE_KEY=private_pem,
            JWT_PUBLIC_KEY=public_pem,
        )
        auth = AuthX(config=config)

        token = auth.create_access_token(uid="timed", expiry=timedelta(hours=1))
        payload = auth._decode_token(token)
        assert payload.sub == "timed"
        assert payload.time_until_expiry.total_seconds() > 3500

    def test_es256_with_additional_data(self):
        private_pem, public_pem = _ec_keypair()
        config = AuthXConfig(
            JWT_ALGORITHM="ES256",
            JWT_PRIVATE_KEY=private_pem,
            JWT_PUBLIC_KEY=public_pem,
        )
        auth = AuthX(config=config)

        token = auth.create_access_token(uid="enriched", data={"role": "editor", "org": "acme"})
        payload = auth._decode_token(token)
        assert payload.sub == "enriched"
        dumped = payload.model_dump()
        assert dumped["role"] == "editor"
        assert dumped["org"] == "acme"

    def test_config_detects_asymmetric_algorithm(self):
        private_pem, public_pem = _rsa_keypair()
        config = AuthXConfig(
            JWT_ALGORITHM="RS256",
            JWT_PRIVATE_KEY=private_pem,
            JWT_PUBLIC_KEY=public_pem,
        )
        assert config.is_algo_asymmetric is True
        assert config.is_algo_symmetric is False

    def test_config_detects_symmetric_algorithm(self):
        config = AuthXConfig(JWT_SECRET_KEY="secret", JWT_ALGORITHM="HS256")
        assert config.is_algo_symmetric is True
        assert config.is_algo_asymmetric is False

    def test_wrong_keypair_fails_decode(self):
        private_pem1, _ = _rsa_keypair()
        _, public_pem2 = _rsa_keypair()
        config = AuthXConfig(
            JWT_ALGORITHM="RS256",
            JWT_PRIVATE_KEY=private_pem1,
            JWT_PUBLIC_KEY=public_pem2,
        )
        auth = AuthX(config=config)

        token = auth.create_access_token(uid="mismatch")
        with pytest.raises(JWTDecodeError):
            auth._decode_token(token)
