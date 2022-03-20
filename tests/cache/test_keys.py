import os

import pytest
import redis

from authx import HTTPCache
from authx.utils.keys import HTTPKeys

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/3")
redis_client = redis.Redis.from_url(REDIS_URL)


class TestHTTPKeys:
    @pytest.mark.asyncio
    async def test_generate_keys(self):
        redis_client.flushdb()
        namespace = "test_namespace"
        HTTPCache.init(redis_url=REDIS_URL, namespace=namespace)
        namespaced_key = await HTTPKeys.generate_key(key="hello", config=HTTPCache)
        assert namespaced_key == f"{namespace}:hello"

    @pytest.mark.asyncio
    async def test_generate_key_with_attr(self):
        redis_client.flushdb()

        class User:
            id: str = "112358"

        user = User()

        namespace = "test_namespace"
        HTTPCache.init(redis_url=REDIS_URL, namespace=namespace)
        namespaced_key = await HTTPKeys.generate_key(
            key="hello.{}", config=HTTPCache, obj=user, obj_attr="id"
        )
        assert namespaced_key == f"{namespace}:hello.112358"

    @pytest.mark.asyncio
    async def test_generate_keys_with_attr(self):
        redis_client.flushdb()

        class User:
            id: str = "112358"

        user = User()

        namespace = "test_namespace"
        HTTPCache.init(redis_url=REDIS_URL, namespace=namespace)
        namespaced_keys = await HTTPKeys.generate_keys(
            keys=["hello.{}", "foo.{}"], config=HTTPCache, obj=user, obj_attr="id"
        )
        namespaced_keys = sorted(namespaced_keys)
        assert namespaced_keys[1] == f"{namespace}:hello.112358"
        assert namespaced_keys[0] == f"{namespace}:foo.112358"
