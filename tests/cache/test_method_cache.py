import os

import pytest
import redis

from authx import HTTPCache, cache

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/3")
redis_client = redis.Redis.from_url(REDIS_URL)

HTTPCache.init(redis_url=REDIS_URL, namespace="test_namespace")


@cache(key="cache.me", ttl_in_seconds=360)
async def cache_me(x: int, invoke_count: int):
    invoke_count += 1
    result = x * 2
    return [result, invoke_count]


async def my_ttl_callable():
    return 3600


@cache(key="cache.me.ttl_callable", ttl_func=my_ttl_callable)
async def cache_me_with_ttl_callable(x: int, invoke_count: int):
    invoke_count += 1
    result = x * 2
    return [result, invoke_count]


@cache(key="cache.me.tz_expire_end_of_day", expire_end_of_day=True)
async def cache_me_with_tz_end_of_day_expiry(x: int, invoke_count: int):
    invoke_count += 1
    result = x * 2
    return [result, invoke_count]


class TestMethodCache:
    @pytest.mark.asyncio
    async def test_method_caching(self):
        redis_client.flushdb()
        invoke_count = 0
        x = await cache_me(x=22, invoke_count=invoke_count)
        y = await cache_me(x=22, invoke_count=invoke_count)
        assert x[0] == y[0]
        assert x[1] == y[1]

    @pytest.mark.asyncio
    async def test_ttl_callable(self):
        redis_client.flushdb()
        HTTPCache.init(redis_url=REDIS_URL, namespace="test_namespace")
        await cache_me_with_ttl_callable(x=22, invoke_count=0)
        await cache_me_with_ttl_callable(x=22, invoke_count=0)
        assert (
            pytest.approx(
                redis_client.ttl("test_namespace:cache.me.ttl_callable"), rel=1e-3
            )
            == 3600
        )
