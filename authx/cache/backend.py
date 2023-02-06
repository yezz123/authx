import json
from typing import Any, Callable, List, Tuple, Union

import redis

from authx.core.expiry import HTTPExpiry
from authx.models.cache import HTTPCache
from authx.utils.logger import log_info


class HTTPCacheBackend:
    def __init__(self, redis: redis.Redis, namespace: str = None):
        self.redis = redis
        self.namespace = namespace or HTTPCache.namespace

    async def set(
        self,
        key: str,
        value: str,
        ttl_in_seconds: int = None,
        ttl_func: Callable = None,
        end_of_day: bool = False,
        end_of_week: bool = False,
    ):
        ttl: int = await HTTPExpiry.get_ttl(
            ttl_in_seconds=ttl_in_seconds,
            end_of_day=end_of_day,
            end_of_week=end_of_week,
            ttl_func=ttl_func,
        )

        stringified_value = json.dumps(value) if type(value) != bytes else value
        with self.redis.pipeline(transaction=True) as pipe:
            pipe.multi()
            pipe.delete(key)
            pipe.set(key, stringified_value, ex=ttl)
            log_info(msg=f"CacheSet: {key}")
            result = pipe.execute()

        del_status, set_status = result

        if del_status:
            log_info(msg=f"CacheClearedOnSet: {key}")

        if set_status:
            log_info(msg=f"CacheSet: {key}")
        return result

    async def get(self, key: str) -> Tuple[Union[int, None], Union[Any, None]]:
        with self.redis.pipeline(transaction=True) as pipe:
            pipe.ttl(key).get(key)
            ttl, result = pipe.execute()

        if result:
            original_val = json.loads(result)
            log_info(msg=f"CacheHit: {key}")
        else:
            original_val = None
        return ttl, original_val

    async def invalidate(self, key: str) -> bool:
        """Invalidates the passed key"""

        with self.redis.pipeline(transaction=True) as pipe:
            pipe.multi()
            pipe.delete(key)
            log_info(msg=f"CacheInvalidated: {key}")
            result = pipe.execute()
        return result

    async def invalidate_all(self, keys: List) -> List[bool]:
        """Invalidates a collection of keys"""

        with self.redis.pipeline(transaction=True) as pipe:
            pipe.multi()
            for key in keys:
                pipe.delete(key)
                log_info(msg=f"CacheInvalidated: {key}")
            return pipe.execute()
