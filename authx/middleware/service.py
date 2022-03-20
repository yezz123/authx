from functools import wraps
from typing import Any, Callable, List

from authx.cache.backend import HTTPCacheBackend
from authx.models.cache import HTTPCache
from authx.utils.keys import HTTPKeys
from authx.utils.logger import log_error


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
                _obj = kwargs.get(f"{obj}", None)
                _key = await HTTPKeys.generate_key(
                    key=key, config=HTTPCache, obj=_obj, obj_attr=obj_attr
                )
                _cache = HTTPCacheBackend(
                    redis=HTTPCache.redis_client, namespace=namespace
                )
                _request = kwargs.get("request", None)
                _response = kwargs.get("response", None)

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
                _cacheable_response = (
                    _computed_response.body
                    if kwargs.get("request", None)
                    else _computed_response
                )

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
    key: str = None,
    keys: List = [],
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
                _obj = kwargs.get(f"{obj}", None)
                _keys = await HTTPKeys.generate_keys(
                    keys=keys, config=HTTPCache, obj=_obj, obj_attr=obj_attr
                )
                _cache = HTTPCacheBackend(
                    redis=HTTPCache.redis_client, namespace=namespace
                )
                await _cache.invalidate_all(keys=_keys)
                _computed_response = await func(*args, **kwargs)
                return _computed_response
            except Exception as e:
                log_error(msg=f"Cache Error: {e}", e=e, method="cache")
                return await func(*args, **kwargs)

        return inner

    return wrapper
