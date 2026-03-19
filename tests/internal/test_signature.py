"""Tests for SignatureSerializer (URL-safe timed serializer)."""

import time

from authx._internal._signature import SignatureSerializer


class TestSignatureSerializerEncodeDecode:
    """Tests for basic encode/decode round-trip."""

    def test_round_trip_simple_dict(self):
        ser = SignatureSerializer("secret", expired_in=0)
        data = {"user_id": 42}
        token = ser.encode(data)
        decoded, err = ser.decode(token)
        assert err is None
        assert decoded == data

    def test_round_trip_complex_dict(self):
        ser = SignatureSerializer("secret", expired_in=0)
        data = {"session_id": 1, "role": "admin", "nested": {"key": "value"}}
        token = ser.encode(data)
        decoded, err = ser.decode(token)
        assert err is None
        assert decoded == data

    def test_round_trip_empty_dict(self):
        ser = SignatureSerializer("secret", expired_in=0)
        data: dict = {}
        token = ser.encode(data)
        decoded, err = ser.decode(token)
        assert err is None
        assert decoded == data

    def test_round_trip_string_values(self):
        ser = SignatureSerializer("secret", expired_in=0)
        data = {"email": "user@example.com", "action": "verify"}
        token = ser.encode(data)
        decoded, err = ser.decode(token)
        assert err is None
        assert decoded["email"] == "user@example.com"

    def test_encode_returns_string(self):
        ser = SignatureSerializer("secret", expired_in=0)
        token = ser.encode({"id": 1})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_different_data_produces_different_tokens(self):
        ser = SignatureSerializer("secret", expired_in=0)
        token1 = ser.encode({"id": 1})
        token2 = ser.encode({"id": 2})
        assert token1 != token2


class TestSignatureSerializerNoExpiry:
    """Tests for serializer with no expiry (expired_in=0)."""

    def test_no_expiry_decode_always_works(self):
        ser = SignatureSerializer("secret", expired_in=0)
        token = ser.encode({"data": "persistent"})
        decoded, err = ser.decode(token)
        assert err is None
        assert decoded == {"data": "persistent"}

    def test_default_expired_in_is_zero(self):
        ser = SignatureSerializer("secret")
        assert ser.expired_in == 0


class TestSignatureSerializerExpiry:
    """Tests for token expiration behavior."""

    def test_valid_within_expiry_window(self):
        ser = SignatureSerializer("secret", expired_in=10)
        token = ser.encode({"id": 1})
        decoded, err = ser.decode(token)
        assert err is None
        assert decoded == {"id": 1}

    def test_expired_token_returns_error(self):
        ser = SignatureSerializer("secret", expired_in=1)
        token = ser.encode({"id": 1})
        time.sleep(2)
        decoded, err = ser.decode(token)
        assert decoded is None
        assert err == "SignatureExpired"


class TestSignatureSerializerInvalidInput:
    """Tests for invalid/tampered tokens and edge cases."""

    def test_none_token_returns_no_token_specified(self):
        ser = SignatureSerializer("secret", expired_in=0)
        decoded, err = ser.decode(None)  # type: ignore[arg-type]
        assert decoded is None
        assert err == "NoTokenSpecified"

    def test_empty_string_returns_bad_signature(self):
        ser = SignatureSerializer("secret", expired_in=0)
        decoded, err = ser.decode("")
        assert decoded is None
        assert err is not None

    def test_garbage_token_returns_error(self):
        ser = SignatureSerializer("secret", expired_in=0)
        decoded, err = ser.decode("not-a-valid-token")
        assert decoded is None
        assert err in ("InvalidSignature", "BadSignature")

    def test_tampered_token_returns_invalid_signature(self):
        ser = SignatureSerializer("secret", expired_in=0)
        token = ser.encode({"id": 1})
        tampered = token[:-4] + "XXXX"
        decoded, err = ser.decode(tampered)
        assert decoded is None
        assert err in ("InvalidSignature", "BadSignature")

    def test_wrong_secret_key_fails(self):
        ser1 = SignatureSerializer("secret-key-1", expired_in=0)
        ser2 = SignatureSerializer("secret-key-2", expired_in=0)
        token = ser1.encode({"id": 1})
        decoded, err = ser2.decode(token)
        assert decoded is None
        assert err in ("InvalidSignature", "BadSignature")


class TestSignatureSerializerDifferentKeys:
    """Tests for key isolation between serializer instances."""

    def test_same_key_can_decode(self):
        ser1 = SignatureSerializer("shared-secret", expired_in=0)
        ser2 = SignatureSerializer("shared-secret", expired_in=0)
        token = ser1.encode({"user": "alice"})
        decoded, err = ser2.decode(token)
        assert err is None
        assert decoded == {"user": "alice"}

    def test_different_keys_cannot_decode(self):
        ser1 = SignatureSerializer("key-alpha", expired_in=0)
        ser2 = SignatureSerializer("key-beta", expired_in=0)
        token = ser1.encode({"user": "alice"})
        decoded, err = ser2.decode(token)
        assert decoded is None
        assert err is not None
