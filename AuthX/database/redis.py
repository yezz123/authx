from typing import Iterable, Optional, Union

from aioredis import Redis


class RedisBackend:
    """
    Setup the Redis connection for the backend using aioredis.

    Returns:
        None
    """

    _redis: Optional[Redis] = None

    def set_client(self, redis: Redis) -> None:
        # TODO: Check if redis is a Redis instance
        self._redis = redis

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

    async def setnx(self, key: str, value: Union[str, bytes, int], expire: int) -> None:
        # TODO: Check if key exists
        await self._redis.setnx(key, value)
        await self._redis.expire(key, expire)
        return None

    async def incr(self, key: str) -> str:
        # TODO: Check if key exists
        return await self._redis.incr(key)

    async def dispatch_action(self, channel: str, action: str, payload: dict) -> None:
        await self._redis.publish_json(channel, {"action": action, "payload": payload})
        return None
