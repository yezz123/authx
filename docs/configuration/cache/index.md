# Redis

**AuthX** provides the necessary tools to work with Redis as a cache thanks to [aio-libs/aioredis-py](https://github.com/aio-libs/aioredis-py) package for full async support.

Setting up the Redis cache is very simple, we just need to create a new instance of the Redis class and pass it to the `set_redis` method.

But first check that you install the required packages:

```shell
pip install authx[redis]
```

Then create a new instance of the Redis class and pass it to the `set_redis` method.

```python
from authx import authx, RedisBackend
import aioredis

auth = authx()

redis = aioredis.from_url("redis://localhost/1")

auth.set_cache(RedisBackend=RedisBackend(redis=redis))
```

- [Operations Provided by Redis](redis.md)
- [HTTPCache](HTTPCache.md)
  - [Example](Example.md)
