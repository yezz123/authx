import time
from typing import Any, Dict

import pytest

from authx._internal import SignatureSerializer


@pytest.fixture
def serializer():
    return SignatureSerializer("TEST_SECRET_KEY", expired_in=1)


def test_encode_decode_success(serializer):
    dict_obj = {"session_id": 1}
    token = serializer.encode(dict_obj)
    data, err = serializer.decode(token)
    assert data is not None and err is None
    assert data["session_id"] == 1


def test_decode_expired_token(serializer):
    dict_obj = {"session_id": 1}
    token = serializer.encode(dict_obj)
    time.sleep(2)  # Wait for token to expire
    data, err = serializer.decode(token)
    assert data is None and err == "SignatureExpired"


def test_decode_invalid_token(serializer):
    invalid_token = "invalid.token.here"
    data, err = serializer.decode(invalid_token)
    assert data is None and err == "InvalidSignature"


def test_decode_none_token(serializer):
    data, err = serializer.decode(None)
    assert data is None and err == "NoTokenSpecified"


def test_decode_tampered_token(serializer):
    dict_obj = {"session_id": 1}
    token = serializer.encode(dict_obj)
    tampered_token = token[:-1] + (
        "1" if token[-1] == "0" else "0"
    )  # Change last character
    data, err = serializer.decode(tampered_token)
    assert data is None and err == "InvalidSignature"


def test_no_expiration():
    non_expiring_serializer = SignatureSerializer("TEST_SECRET_KEY", expired_in=0)
    dict_obj = {"session_id": 1}
    token = non_expiring_serializer.encode(dict_obj)
    time.sleep(2)  # Wait, but token should not expire
    data, err = non_expiring_serializer.decode(token)
    assert data is not None and err is None
    assert data["session_id"] == 1


def test_different_secret_keys():
    serializer1 = SignatureSerializer("SECRET_KEY_1")
    serializer2 = SignatureSerializer("SECRET_KEY_2")
    dict_obj = {"session_id": 1}
    token = serializer1.encode(dict_obj)
    data, err = serializer2.decode(token)
    assert data is None and err == "InvalidSignature"


def test_large_payload():
    serializer = SignatureSerializer("TEST_SECRET_KEY")
    large_dict = {
        f"key_{i}": "x" * 1000 for i in range(100)
    }  # 100 keys with 1000 character values
    token = serializer.encode(large_dict)
    data, err = serializer.decode(token)
    assert data == large_dict and err is None


def test_empty_dict():
    serializer = SignatureSerializer("TEST_SECRET_KEY")
    empty_dict: Dict[str, Any] = {}
    token = serializer.encode(empty_dict)
    data, err = serializer.decode(token)
    assert data == empty_dict and err is None


def test_malformed_token():
    serializer = SignatureSerializer("TEST_SECRET_KEY")
    malformed_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."  # Incomplete token
    data, err = serializer.decode(malformed_token)
    assert data is None and err == "BadSignature"
