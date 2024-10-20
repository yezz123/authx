import datetime

import jwt
import pytest

from authx.exceptions import (
    CSRFError,
    FreshTokenRequiredError,
    JWTDecodeError,
    RefreshTokenRequiredError,
    TokenTypeError,
)
from authx.schema import PYDANTIC_V2, RequestToken, TokenPayload


@pytest.fixture(scope="function")
def valid_payload():
    return TokenPayload(
        type="access",
        fresh=True,
        sub="BOOOM",
        csrf="CSRF_TOKEN",
        scopes=["read", "write"],
        exp=datetime.timedelta(minutes=20),
        nbf=datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc),
        iat=datetime.datetime(
            2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc
        ).timestamp(),
    )


@pytest.fixture(scope="function")
def valid_refresh_payload():
    return TokenPayload(
        type="refresh",
        fresh=True,
        sub="BOOOM",
        csrf="CSRF_TOKEN",
        scopes=["read", "write"],
        exp=datetime.timedelta(minutes=20),
        nbf=datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc),
        iat=datetime.datetime(
            2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc
        ).timestamp(),
    )


@pytest.fixture(scope="function")
def invalid_payload():
    return TokenPayload(
        type="false",
        fresh=False,
        sub="BOOOM",
        csrf="CSRF_TOKEN",
        iat=datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc),
        exp=datetime.datetime(2000, 1, 1, 14, 0, tzinfo=datetime.timezone.utc),
    )


@pytest.fixture(scope="function")
def valid_token(valid_payload: TokenPayload):
    KEY = "SECRET"
    ALGO = "HS256"
    return RequestToken(
        token=valid_payload.encode(KEY, ALGO),
        csrf=valid_payload.csrf,
        type="access",
        location="cookies",
    )


@pytest.fixture(scope="function")
def invalid_token(invalid_payload: TokenPayload):
    KEY = "SECRET"
    ALGO = "HS256"
    return RequestToken(
        token=invalid_payload.encode(KEY, ALGO),
        csrf="EXPECTED_CSRF",
        type="access",
        location="cookies",
    )


@pytest.fixture(scope="function")
def invalid_refresh_token(valid_payload: TokenPayload):
    KEY = "SECRET"
    ALGO = "HS256"
    return RequestToken(
        token=valid_payload.encode(KEY, ALGO),
        csrf="EXPECTED_CSRF",
        type="refresh",
        location="cookies",
    )


@pytest.fixture(scope="function")
def sample_payload():
    return {
        "sub": "1234567890",
        "name": "John Doe",
        "iat": int(datetime.datetime.now().timestamp()),
        "exp": int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp()),
        "type": "access",
        "fresh": True,
        "jti": "unique-identifier",
        "scopes": ["read", "write"],
    }


def test_payload_has_scopes(valid_payload: TokenPayload):
    assert valid_payload.has_scopes("read")
    assert valid_payload.has_scopes("read", "write")
    assert valid_payload.has_scopes("admin") is False
    assert valid_payload.has_scopes("admin", "read") is False


def test_payload_encode(valid_payload: TokenPayload):
    KEY = "SECRET"
    ALGO = "HS256"
    token = valid_payload.encode(KEY, ALGO)
    assert isinstance(token, str)


def test_payload_decode(valid_payload: TokenPayload):
    KEY = "SECRET"
    ALGO = "HS256"
    token = valid_payload.encode(KEY, ALGO)
    payload = TokenPayload.decode(token, KEY, algorithms=[ALGO], verify=True)
    assert payload.sub == valid_payload.sub
    assert payload.nbf == valid_payload.nbf
    assert payload.exp == valid_payload.exp


def test_token_verify_valid(valid_token: RequestToken):
    KEY = "SECRET"
    ALGO = "HS256"

    valid_token.verify(
        KEY,
        [ALGO],
        verify_jwt=True,
        verify_type=False,
        verify_csrf=False,
        verify_fresh=False,
    )
    valid_token.verify(
        KEY,
        [ALGO],
        verify_jwt=True,
        verify_type=True,
        verify_csrf=False,
        verify_fresh=False,
    )
    valid_token.verify(
        KEY,
        [ALGO],
        verify_jwt=True,
        verify_type=True,
        verify_csrf=True,
        verify_fresh=True,
    )


def test_token_verify_invalid(invalid_token: RequestToken):
    KEY = "SECRET"
    ALGO = "HS256"
    with pytest.raises(JWTDecodeError):
        invalid_token.verify(
            KEY,
            [ALGO],
            verify_jwt=True,
            verify_type=False,
            verify_csrf=False,
            verify_fresh=False,
        )
    with pytest.raises(TokenTypeError):
        invalid_token.verify(
            KEY,
            [ALGO],
            verify_jwt=False,
            verify_type=True,
            verify_csrf=False,
            verify_fresh=False,
        )
    with pytest.raises(CSRFError):
        invalid_token.verify(
            KEY,
            [ALGO],
            verify_jwt=False,
            verify_type=False,
            verify_csrf=True,
            verify_fresh=False,
        )
    with pytest.raises(FreshTokenRequiredError):
        invalid_token.verify(
            KEY,
            [ALGO],
            verify_jwt=False,
            verify_type=False,
            verify_csrf=False,
            verify_fresh=True,
        )


def test_token_verify_none_csrf_exception(invalid_token: RequestToken):
    KEY = "SECRET"
    ALGO = "HS256"

    invalid_token.csrf = None
    with pytest.raises(CSRFError):
        invalid_token.verify(
            KEY,
            [ALGO],
            verify_jwt=False,
            verify_type=False,
            verify_csrf=True,
            verify_fresh=False,
        )
    invalid_token.csrf = "CSRF_TOKEN"


def test_invalid_refresh_type_exception(invalid_refresh_token: RequestToken):
    KEY = "SECRET"
    ALGO = "HS256"
    with pytest.raises(RefreshTokenRequiredError):
        invalid_refresh_token.verify(
            KEY,
            [ALGO],
            verify_jwt=True,
            verify_type=True,
            verify_csrf=True,
            verify_fresh=False,
        )


def test_token_verify_none_csrf_claim_exception():
    KEY = "SECRET"
    ALGO = "HS256"

    payload = TokenPayload(
        type="false",
        fresh=False,
        sub="BOOOM",
        csrf=None,
        iat=datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc),
    )

    token = RequestToken(
        token=payload.encode(KEY, ALGO),
        csrf="EXPECTED_CSRF",
        type="access",
        location="cookies",
    )
    with pytest.raises(CSRFError):
        token.verify(
            KEY,
            [ALGO],
            verify_jwt=False,
            verify_type=False,
            verify_csrf=True,
            verify_fresh=False,
        )


def test_validation_error_on_verify():
    KEY = "SECRET"
    ALGO = "HS256"

    bad_payload = {"iat": "hello"}
    token = jwt.encode(bad_payload, KEY, ALGO)
    rqt = RequestToken(token=token, type="access", location="headers", csrf=None)

    with pytest.raises(JWTDecodeError):
        rqt.verify(
            key=KEY,
            algorithms=[ALGO],
            verify_csrf=False,
            verify_fresh=False,
            verify_type=False,
            verify_jwt=False,
        )


def test_payload_issued_at_property(valid_payload: TokenPayload):
    # Test when 'iat' is a float
    assert isinstance(valid_payload.issued_at, datetime.datetime)

    # Test when 'iat' is an int
    valid_payload.iat = int(valid_payload.iat)
    assert isinstance(valid_payload.issued_at, datetime.datetime)

    # Test when 'iat' is a datetime object
    valid_payload.iat = datetime.datetime.now(datetime.timezone.utc)
    assert isinstance(valid_payload.issued_at, datetime.datetime)

    # Test when 'iat' is not a supported type
    invalid_payload = valid_payload.copy()
    invalid_payload.iat = "invalid"
    with pytest.raises(TypeError):
        invalid_payload.issued_at


def test_payload_expiry_datetime_property(valid_payload: TokenPayload):
    # Test when 'exp' is a datetime object
    assert isinstance(valid_payload.expiry_datetime, datetime.datetime)

    # Test when 'exp' is a timedelta object
    valid_payload.exp = datetime.timedelta(minutes=20)
    assert isinstance(valid_payload.expiry_datetime, datetime.datetime)

    assert isinstance(valid_payload.expiry_datetime, datetime.datetime)

    # Test when 'exp' is not a supported type
    invalid_payload = valid_payload.copy()
    invalid_payload.exp = "invalid"
    with pytest.raises(TypeError):
        invalid_payload.expiry_datetime


def test_payload_time_until_expiry_property(valid_payload: TokenPayload):
    assert isinstance(valid_payload.time_until_expiry, datetime.timedelta)


def test_payload_time_since_issued_property(valid_payload: TokenPayload):
    assert isinstance(valid_payload.time_since_issued, datetime.timedelta)


def test_payload_has_scopes_valid(valid_payload: TokenPayload):
    assert valid_payload.has_scopes("read")
    assert valid_payload.has_scopes("read", "write")
    assert not valid_payload.has_scopes("admin")
    assert not valid_payload.has_scopes("admin", "read")


def test_payload_has_scopes_empty(valid_payload: TokenPayload):
    valid_payload.scopes = []
    assert not valid_payload.has_scopes("read")
    assert not valid_payload.has_scopes("read", "write")


@pytest.mark.skipif(not PYDANTIC_V2, reason="Test for Pydantic V2")
def test_payload_extra_dict_pydantic_v2():
    payload = TokenPayload(
        type="access",
        fresh=True,
        sub="BOOOM",
        csrf="CSRF_TOKEN",
        scopes=["read", "write"],
        exp=datetime.timedelta(minutes=20),
        nbf=datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc),
        iat=datetime.datetime(
            2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc
        ).timestamp(),
        extra="EXTRA",
    )
    assert payload.extra_dict == {}


@pytest.mark.skipif(PYDANTIC_V2, reason="Test for Pydantic V1")
def test_payload_extra_dict_pydantic_v1():
    payload = TokenPayload(
        type="access",
        fresh=True,
        sub="BOOOM",
        csrf="CSRF_TOKEN",
        scopes=["read", "write"],
        exp=datetime.timedelta(minutes=20),
        nbf=datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc),
        iat=datetime.datetime(
            2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc
        ).timestamp(),
        extra="EXTRA",
    )
    assert payload.extra_dict == {"extra": "EXTRA"}


def test_verify_token_type_exception():
    KEY = "SECRET"
    ALGO = "HS256"

    payload = TokenPayload(
        type="false",
        fresh=False,
        sub="BOOOM",
        csrf=None,
        iat=datetime.datetime(2000, 1, 1, 12, 0, tzinfo=datetime.timezone.utc),
    )

    token = RequestToken(
        token=payload.encode(KEY, ALGO),
        csrf="EXPECTED_CSRF",
        type="access",
        location="cookies",
    )
    with pytest.raises(TokenTypeError):
        token.verify(
            KEY,
            [ALGO],
            verify_jwt=True,
            verify_type=True,
            verify_csrf=True,
            verify_fresh=False,
        )


def test_token_payload_creation(sample_payload):
    payload = TokenPayload(**sample_payload)
    assert payload.sub == "1234567890"
    assert payload.type == "access"
    assert payload.scopes == ["read", "write"]


@pytest.mark.skipif(not PYDANTIC_V2, reason="Test for Pydantic V2")
def test_token_payload_extra_fields_pydantic_v2(sample_payload):
    sample_payload["extra_field"] = "extra_value"
    payload = TokenPayload(**sample_payload)
    assert payload.extra_dict == {}


@pytest.mark.skipif(PYDANTIC_V2, reason="Test for Pydantic V1")
def test_token_payload_extra_fields_pydantic_v1(sample_payload):
    sample_payload["extra_field"] = "extra_value"
    payload = TokenPayload(**sample_payload)
    assert payload.extra_dict == {"extra_field": "extra_value", "name": "John Doe"}


def test_token_payload_encode_decode():
    payload = TokenPayload(sub="1234567890", type="access")
    encoded = payload.encode("secret_key")
    decoded = TokenPayload.decode(encoded, "secret_key")
    assert decoded.sub == "1234567890"
    assert decoded.type == "access"


def test_token_payload_expiry():
    payload = TokenPayload(
        sub="1234567890", exp=datetime.datetime.now() + datetime.timedelta(hours=1)
    )
    assert isinstance(payload.expiry_datetime, datetime.datetime)
    assert isinstance(payload.time_until_expiry, datetime.timedelta)


def test_token_payload_issued_at():
    now = datetime.datetime.now()
    payload = TokenPayload(sub="1234567890", iat=now.timestamp())
    assert isinstance(payload.issued_at, datetime.datetime)
    assert isinstance(payload.time_since_issued, datetime.timedelta)


def test_token_payload_scopes():
    payload = TokenPayload(sub="1234567890", scopes=["read", "write"])
    assert payload.has_scopes("read")
    assert payload.has_scopes("read", "write")
    assert not payload.has_scopes("admin")


def test_token_payload_invalid_decode():
    with pytest.raises(JWTDecodeError):
        TokenPayload.decode("invalid_token", "secret_key")


def test_token_payload_nbf_validator():
    future_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    payload = TokenPayload(sub="1234567890", nbf=future_time)
    assert isinstance(payload.nbf, float)
    assert payload.nbf == pytest.approx(future_time.timestamp(), abs=1)
