from datetime import datetime

import pytest

from AuthX.core.jwt import JWTBackend

from tests.utils import MockCacheBackend, private_key, public_key

jwt_backend = JWTBackend(MockCacheBackend(), private_key, public_key, 60, 60 * 10)

sample_access_token = jwt_backend.create_access_token({"id": 1})
sample_refresh_token = jwt_backend.create_refresh_token({})

sample_expired_access_token = jwt_backend._create_token({}, "access", -60)
sample_expired_refresh_token = jwt_backend._create_token({}, "refresh", -60)


@pytest.mark.asyncio
async def test_create_token():
    token = jwt_backend._create_token({}, "access")
    payload = await jwt_backend.decode_token(token)
    assert int(payload.get("exp")) - int(payload.get("iat")) == 60  # ???


@pytest.mark.asyncio
async def test_decode_token():
    payload = await jwt_backend.decode_token(None)
    assert payload is None

    payload = await jwt_backend.decode_token("AAAAAA")
    assert payload is None

    payload = await jwt_backend.decode_token(sample_access_token)
    assert payload is not None

    payload = await jwt_backend.decode_token(sample_refresh_token)
    assert payload is not None

    payload = await jwt_backend.decode_token(sample_expired_access_token)
    assert payload is None

    payload = await jwt_backend.decode_token(sample_expired_refresh_token)
    assert payload is None


@pytest.mark.asyncio
async def test_create_access_token():
    access_token = jwt_backend.create_access_token({})
    payload = await jwt_backend.decode_token(access_token)
    assert int(payload.get("iat")) < int(payload.get("exp"))
    assert payload.get("type") == "access"


@pytest.mark.asyncio
async def test_create_refresh_token():
    refresh_token = jwt_backend.create_refresh_token({})
    payload = await jwt_backend.decode_token(refresh_token)
    assert int(payload.get("iat")) < int(payload.get("exp"))
    assert payload.get("type") == "refresh"


def test_create_tokens():
    tokens = jwt_backend.create_tokens({})

    assert tokens.get("access") is not None
    assert tokens.get("refresh") is not None


@pytest.mark.asyncio
async def test_blackout():
    key = "users:blackout"
    epoch = datetime.utcfromtimestamp(0)
    ts = int((datetime.utcnow() - epoch).total_seconds()) + 10
    await jwt_backend._cache.set(key, ts, 10)
    payload = await jwt_backend.decode_token(sample_access_token)
    assert payload is None
    await jwt_backend._cache.delete(key)


@pytest.mark.asyncio
async def test_logout():
    key = "users:kick:1"
    epoch = datetime.utcfromtimestamp(0)
    ts = int((datetime.utcnow() - epoch).total_seconds()) + 10
    await jwt_backend._cache.set(key, ts, 10)
    payload = await jwt_backend.decode_token(sample_access_token)
    assert payload is None
    await jwt_backend._cache.delete(key)
