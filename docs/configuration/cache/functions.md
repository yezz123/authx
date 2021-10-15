# Redis Provider

## Initial the Redis Class

Redis is a good choice for caching, that why we need to use it, maybe to store the token or users data some configuration relate to cache.

In Python we use [`aioredis`](https://aioredis.readthedocs.io/en/stable/) library to connect to Redis.

```python
def set_client(self, redis: Redis) -> None:
        self._redis = redis
```

### Redis CRUD

Redis Crud is a simple CRUD operation, we can use it to store the data in Redis. we need to create some methods. (Get Key Value, Set Key Value, Delete Key, etc.)

```py
async def get(self, key: str) -> str:
        return await self._redis.get(key)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)
        return None

    async def keys(self, match: str) -> Iterable[str]:
        return await self._redis.keys(match)

    async def set(
        self, key: str, value: Union[str, bytes, int], expire: int = 0
    ) -> None:
        await self._redis.set(key, value, expire=expire)
        return None
```

!!! warning
    It is very important not to `await` buffered command (ie `self._redis.set('foo', '123')`) as it will block forever.

### Dispatch Action

After we have the client we need to dispatch the action to the client, this gonna help to publish `.json` file to the client.

```py
async def dispatch_action(
    self, channel: str,
    action: str,
    payload: dict) -> None:
        await self._redis.publish_json(channel,
        {"action": action, "payload": payload})
        return None
```
