# HTTP Cache Using Redis

!!! warning
     You need to install dependencies to use The HTTP Cache.

## Overview

HTTP caching occurs when the browser stores local copies of web resources for
faster retrieval the next time the resource is required. As your application
serves resources it can attach cache headers to the response specifying the
desired cache behavior.

![Overview](https://devcenter1.assets.heroku.com/article-images/782-imported-1443570279-782-imported-1443554749-55-original.jpg)

When an item is fully cached, the browser may choose to not contact the server
at all and simply use its own cached copy:

![Overview](https://devcenter1.assets.heroku.com/article-images/782-imported-1443570282-782-imported-1443554751-54-original.jpg)

## HTTP cache headers

There are two primary cache headers, `Cache-Control` and `Expires`.

### Cache-Control

The `Cache-Control` header is the most important header to set as it effectively
`switches on` caching in the browser. With this header in place, and set with a
value that enables caching, the browser will cache the file for as long as
specified. Without this header the browser will re-request the file on each
subsequent request.

### Expires

When accompanying the `Cache-Control` header, Expires simply sets a date from
which the cached resource should no longer be considered valid. From this date
forward the browser will request a fresh copy of the resource.

> This Introduction to HTTP Caching is based on the
> [HTTP Caching Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching).

AuthX provide a simple HTTP caching model designed to work with
[FastAPI](https://fastapi.tiangolo.com/),

## How to install

Make sure to have the necessary dependencies installed:

<div class="termy">

```console
$ pip install authx_extra

---> 100%
```

</div>

## Initialize the cache

```python
import os
import redis
from authx_extra.cache import HTTPCache
from pytz import timezone

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/3")
redis_client = redis.Redis.from_url(REDIS_URL)

africa_Casablanca = timezone('Africa/Casablanca')

HTTPCache.init(redis_url=REDIS_URL, namespace='test_namespace', tz=africa_Casablanca)
```

The `tz` attribute becomes import when the `cache` decorator relies on the
`expire_end_of_day` and `expire_end_of_week` attributes to expire the cache key.

## Define your controllers

The `ttl_in_seconds` expires the cache in 180 seconds. There are other
approaches to take with helpers like `expire_end_of_day` and
`expires_end_of_week`

```python
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from authx_extra.cache import HTTPCache, cache

@app.get("/b/home")
@cache(key="b.home", ttl_in_seconds=180)
async def home(request: Request, response: Response):
    return JSONResponse({"page": "home", "datetime": str(datetime.utcnow())})

@app.get("/b/welcome")
@cache(key="b.home", end_of_week=True)
async def home(request: Request, response: Response):
    return JSONResponse({"page": "welcome", "datetime": str(datetime.utcnow())})
```

### Building keys from parameter objects

While it's always possible to explicitly pass keys onto the `key` attribute,
there are scenarios where the keys need to be built based on the parameters
received by the controller method. For instance, in an authenticated API where
the `user_id` is fetched as a controller `Depends` argument.

```python
class User:
    id: str = "112358"

user = User()

@app.get("/b/logged-in")
@cache(key="b.logged_in.{}", obj="user", obj_attr="id")
async def logged_in(request: Request, response: Response, user=user):
    return JSONResponse(
        {"page": "home", "user": user.id, "datetime": str(datetime.utcnow())}
    )
```

In the example above, the key allows room for a dynamic attribute fetched from
the object `user`. The key eventually becomes `b.logged_in.112358` if the
`user.id` returns `112358`

### Explicitly invalidating the cache

The cache invalidation can be managed using the `@invalidate_cache` decorator.

```python
class User:
    id: str = "112358"

user = User()

@app.post("/b/logged-in")
@invalidate_cache(
    key="b.logged_in.{}", obj="user", obj_attr="id", namespace="test_namespace"
)
async def post_logged_in(request: Request, response: Response, user=user):
    return JSONResponse(
        {"page": "home", "user": user.id, "datetime": str(datetime.utcnow())}
    )
```

### Invalidating more than one key at a time

The cache invalidation decorator allows for multiple keys to be invalidated in
the same call. However, the it assumes that the object attributes generated
apply all keys.

```python
class User:
    id: str = "112358"

user = User()

@app.post("/b/logged-in")
@invalidate_cache(
    keys=["b.logged_in.{}", "b.profile.{}"], obj="user", obj_attr="id", namespace="test_namespace"
)
async def post_logged_in(request: Request, response: Response, user=user):
    return JSONResponse(
        {"page": "home", "user": user.id, "datetime": str(datetime.utcnow())}
    )
```

## Computing `ttl` dynamically for cache keys using a `Callable`

A callable can be passed as part of the decorator to dynamically compute what
the ttl for a cache key should be. For example

```python
async def my_ttl_callable() -> int:
    return 3600

@app.get('/b/ttl_callable')
@cache(key='b.ttl_callable_expiry', ttl_func=my_ttl_callable)
async def path_with_ttl_callable(request: Request, response: Response):
    return JSONResponse(
        {"page": "path_with_ttl_callable", "datetime": str(datetime.utcnow())}
    )
```

The `ttl_func` is always assumed to be an **async** method

## Caching methods that aren't controllers

HTTPCache works exactly the same way with regular methods. The example below
explains usage of the cache in service objects and application services.

```py
import os
import redis
from authx_extra.cache import HTTPCache, cache, invalidate_cache

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/3")
redis_client = redis.Redis.from_url(REDIS_URL)

class User:
    id: str = "112358"

user = User()


HTTPCache.init(redis_url=REDIS_URL, namespace='test_namespace')


@cache(key='cache.me', ttl_in_seconds=360)
async def cache_me(x:int, invoke_count:int):
    invoke_count = invoke_count + 1
    result = x * 2
    return [result, invoke_count]
```
