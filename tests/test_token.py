import time
import unittest
from datetime import datetime, timedelta, timezone

import pytest

from authx.exceptions import JWTDecodeError
from authx.token import create_token, decode_token


def test_create_token():
    token = create_token(
        uid="TEST", key="SECRET", algorithm="HS256", type="TYPE", csrf=False
    )
    assert isinstance(token, str)


@unittest.skip("Weird Behavior at the level of pytest.raises(JWTDecodeError)")
def test_encode_decode_token():
    KEY = "SECRET"
    ALGO = "HS256"
    with pytest.raises(JWTDecodeError):
        token = create_token(
            uid="TEST", key=KEY, algorithm=ALGO, type="TYPE", csrf=False
        )
        decode_token(token, key=KEY, algorithms=[ALGO])

    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)

    assert "sub" in payload
    assert "jti" in payload
    assert "type" in payload
    assert "iat" in payload
    assert payload.get("sub") == "TEST"
    assert payload.get("type") == "TYPE"
    assert payload.get("iat") is not None
    assert payload.get("jti") is not None
    assert isinstance(payload.get("iat"), float)
    assert isinstance(payload.get("jti"), str)


def test_create_token_with_iat_claims():
    KEY = "SECRET"
    ALGO = "HS256"

    now = datetime.now(tz=timezone.utc)

    # Issued as datetime.datetime
    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        csrf=False,
        issued=now,
    )
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)

    assert payload.get("iat") is not None
    assert isinstance(payload.get("iat"), float)
    assert datetime.fromtimestamp(payload.get("iat"), tz=timezone.utc) == now

    # Issued as datetime.datetime
    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        csrf=False,
        issued=1678225769.943363,
    )
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)

    assert payload.get("iat") is not None
    assert isinstance(payload.get("iat"), float)
    assert int(payload.get("iat")) == int(1678225769.943363)


@pytest.mark.parametrize("claim,argument", [("exp", "expiry"), ("nbf", "not_before")])
def test_create_token_with_timed_claims(claim, argument):
    KEY = "SECRET"
    ALGO = "HS256"

    # Expiry as datetime.datetime
    now = datetime.now(tz=timezone.utc)
    token = create_token(
        uid="TEST", key=KEY, algorithm=ALGO, type="TYPE", csrf=False, **{argument: now}
    )
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)

    assert payload.get(claim) is not None
    assert isinstance(payload.get(claim), float)
    assert datetime.fromtimestamp(payload.get(claim), tz=timezone.utc) == now

    # Expiry as numeric
    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        csrf=False,
        **{argument: 1678225769.943363},
    )
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)

    assert payload.get(claim) is not None
    assert isinstance(payload.get(claim), float)
    assert int(payload.get(claim)) == int(1678225769.943363)

    # Expiry as numeric
    now = datetime.now(tz=timezone.utc)
    dt = timedelta(minutes=10)
    token = create_token(
        uid="TEST", key=KEY, algorithm=ALGO, type="TYPE", csrf=False, **{argument: dt}
    )
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)

    assert payload.get(claim) is not None
    assert isinstance(payload.get(claim), float)
    assert abs((now + dt).timestamp() - payload.get(claim)) < 1


def test_create_token_with_fresh_claims():
    KEY = "SECRET"
    ALGO = "HS256"

    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        fresh=True,
        csrf=False,
    )
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)

    assert payload.get("fresh") is None

    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="access",
        fresh=True,
        csrf=False,
    )
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)
    assert payload.get("fresh") is not None
    assert payload.get("fresh") is True


def test_create_token_with_additional_claims():
    KEY = "SECRET"
    ALGO = "HS256"

    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        csrf=False,
        additional_data={"sub": "OVERRIDE", "foo": "bar"},
        ignore_errors=True,
    )
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)
    assert payload.get("sub") == "TEST"
    assert payload.get("foo") == "bar"


def test_create_token_with_issuer():
    KEY = "SECRET"
    ALGO = "HS256"

    iat = datetime(2000, 1, 1, 12, 0)

    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        csrf=False,
        issued=iat,
        issuer="TESTING",
    )

    with pytest.raises(JWTDecodeError):
        decode_token(
            token, key=KEY, algorithms=[ALGO], verify=True, issuer="BAD_ISSUER"
        )

    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=True)
    assert payload.get("iss") == "TESTING"
    payload = decode_token(
        token, key=KEY, algorithms=[ALGO], verify=True, issuer="TESTING"
    )
    assert payload.get("iss") == "TESTING"


def test_create_token_with_audience():
    KEY = "SECRET"
    ALGO = "HS256"

    iat = datetime(2000, 1, 1, 12, 0)

    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        csrf=False,
        issued=iat,
        audience=["TESTING", "AUTHX"],
    )

    with pytest.raises(JWTDecodeError):
        decode_token(
            token, key=KEY, algorithms=[ALGO], verify=True, audience="BAD_AUDIENCE"
        )
        decode_token(token, key=KEY, algorithms=[ALGO], verify=True)

    payload = decode_token(
        token, key=KEY, algorithms=[ALGO], verify=True, audience=["TESTING"]
    )
    payload = decode_token(
        token, key=KEY, algorithms=[ALGO], verify=True, audience="TESTING"
    )
    payload = decode_token(
        token, key=KEY, algorithms=[ALGO], verify=True, audience=["AUTHX"]
    )
    payload = decode_token(
        token, key=KEY, algorithms=[ALGO], verify=True, audience="AUTHX"
    )
    payload = decode_token(
        token, key=KEY, algorithms=[ALGO], verify=True, audience=["TESTING", "AUTHX"]
    )
    assert payload.get("aud") == ["TESTING", "AUTHX"]


def test_create_token_with_csrf_claim():
    KEY = "SECRET"
    ALGO = "HS256"

    token = create_token(uid="TEST", key=KEY, algorithm=ALGO, type="TYPE", csrf=False)
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)
    assert payload.get("csrf") is None

    token = create_token(uid="TEST", key=KEY, algorithm=ALGO, type="TYPE", csrf=True)
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)
    assert payload.get("csrf") is not None
    assert isinstance(payload.get("csrf"), str)

    token = create_token(uid="TEST", key=KEY, algorithm=ALGO, type="TYPE", csrf="Test")
    payload = decode_token(token, key=KEY, algorithms=[ALGO], verify=False)
    assert payload.get("csrf") is not None
    assert isinstance(payload.get("csrf"), str)
    assert payload.get("csrf") == "Test"


@pytest.mark.parametrize(
    "claim", ["fresh", "csrf", "iat", "exp", "iss", "aud", "type", "jti", "nbf", "sub"]
)
def test_create_token_with_additional_claims_exception(claim):
    KEY = "SECRET"
    ALGO = "HS256"

    with pytest.raises(ValueError):
        create_token(
            uid="TEST",
            key=KEY,
            algorithm=ALGO,
            type="TYPE",
            csrf=False,
            additional_data={claim: "OVERRIDE"},
            ignore_errors=False,
        )


@unittest.skip("Weird Behavior at the level of pytest.raises(JWTDecodeError)")
def test_verify_token():
    KEY = "SECRET"
    ALGO = "HS256"
    SLEEP_TIME = 2

    # Test iat Error
    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        csrf=False,
    )
    with pytest.raises(JWTDecodeError):
        decode_token(token, key=KEY, algorithms=[ALGO], verify=True)

    # Test iat Valid
    iat = datetime(2000, 1, 1, 12, 0)
    token = create_token(
        uid="TEST", key=KEY, algorithm=ALGO, type="TYPE", csrf=False, issued=iat
    )
    decode_token(token, key=KEY, algorithms=[ALGO], verify=True)

    # Test exp Valid
    exp = timedelta(seconds=SLEEP_TIME)
    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        csrf=False,
        issued=iat,
        expiry=exp,
    )
    decode_token(token, key=KEY, algorithms=[ALGO], verify=True)
    time.sleep(SLEEP_TIME)
    with pytest.raises(JWTDecodeError):
        decode_token(token, key=KEY, algorithms=[ALGO], verify=True)

    # Test nbf Valid
    nbf = timedelta(seconds=SLEEP_TIME)
    token = create_token(
        uid="TEST",
        key=KEY,
        algorithm=ALGO,
        type="TYPE",
        csrf=False,
        issued=iat,
        not_before=nbf,
    )
    with pytest.raises(JWTDecodeError):
        decode_token(token, key=KEY, algorithms=[ALGO], verify=True)
    time.sleep(SLEEP_TIME)
    decode_token(token, key=KEY, algorithms=[ALGO], verify=True)
