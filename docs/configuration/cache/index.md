# Redis

**AuthX** provides the necessary tools to work with Redis as a cache thanks to
[redis/redis-py](https://github.com/redis/redis-py) package for full
async support.

Setting up the Redis cache is very simple, we just need to create a new instance
of the Redis class and pass it to the `set_redis` method.

- But first check that you install the required packages

- Then create a new instance of the Redis class and pass it to the `set_redis`
  method.

```python
from authx import authx, RedisBackend
from redis import asyncio as Redis

auth = authx()

redis = Redis(host="localhost", port=6379, db=1)

auth.set_cache(RedisBackend=RedisBackend(redis=redis))
```

- [Operations Provided by Redis](redis.md)
- [HTTPCache](HTTPCache.md)
  - [Example](Example.md)
