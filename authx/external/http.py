import json
from functools import wraps
from typing import Any, Callable, List, Tuple, Union

import redis

from authx._internal import HTTPCache, log_error, log_info
from authx.external.cache import HTTPExpiry, HTTPKeys


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


def cache(
    key: str,
    obj: Any = None,
    obj_attr: str = None,
    ttl_in_seconds: int = None,
    expire_end_of_day: bool = True,
    expire_end_of_week: bool = False,
    ttl_func: Callable = None,
    namespace: str = None,
):
    """Decorator method that sets the return value to cache before returning."""
    if not namespace:
        namespace = HTTPCache.namespace

    def wrapper(func: Callable):
        @wraps(func)
        async def inner(*args, **kwargs):
            try:
                # extracts the `id` attribute from the `obj_attr` parameter passed to the `@cache` method
                _obj = kwargs.get(f"{obj}")
                _key = await HTTPKeys.generate_key(key=key, config=HTTPCache, obj=_obj, obj_attr=obj_attr)
                _cache = HTTPCacheBackend(redis=HTTPCache.redis_client, namespace=namespace)
                _request = kwargs.get("request")
                _response = kwargs.get("response")

                # check cache and return if value is present
                ttl, response = await _cache.get(key=_key)
                if response:
                    if _request and _response:
                        _response.headers["Cache-Control"] = f"max-age={ttl}"
                        _response.headers["Cache-Hit"] = "true"
                    return response

                # if not a cache-hit populate current response.
                _computed_response = await func(*args, **kwargs)

                # if http request store the response body data
                _cacheable_response = _computed_response.body if kwargs.get("request", None) else _computed_response

                await _cache.set(
                    key=_key,
                    value=_cacheable_response,
                    ttl_in_seconds=ttl_in_seconds,
                    ttl_func=ttl_func,
                    end_of_day=expire_end_of_day,
                    end_of_week=expire_end_of_week,
                )
                return _computed_response
            except Exception as e:
                log_error(msg=f"Cache Error: {e}", e=e, method="cache")
                return await func(*args, **kwargs)

        return inner

    return wrapper


def invalidate_cache(
    key: str = [],
    keys: List = None,
    obj: Any = None,
    obj_attr: str = None,
    namespace: str = None,
):
    """Invalidates a specific cache key"""

    if not namespace:
        namespace = HTTPCache.namespace

    if key:
        keys = [key]

    def wrapper(func: Callable):
        @wraps(func)
        async def inner(*args, **kwargs):
            try:
                # extracts the `id` attribute from the `obj_attr` giparameter passed to the `@cache` method
                _obj = kwargs.get(f"{obj}")
                _keys = await HTTPKeys.generate_keys(keys=keys, config=HTTPCache, obj=_obj, obj_attr=obj_attr)
                _cache = HTTPCacheBackend(redis=HTTPCache.redis_client, namespace=namespace)
                await _cache.invalidate_all(keys=_keys)
                _computed_response = await func(*args, **kwargs)
                return _computed_response
            except Exception as e:
                log_error(msg=f"Cache Error: {e}", e=e, method="cache")
                return await func(*args, **kwargs)

        return inner

    return wrapper
