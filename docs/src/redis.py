import asyncio

import aioredis

from authx import Authentication


async def cache():
    """
    This example demonstrates how to use Redis Pub/Sub.
    """
    link = "redis://localhost"
    redis = aioredis.from_url(link)
    await redis.set("my-key", "value")
    value = await redis.get("my-key")
    print(value)


asyncio.run(cache())

Authentication.set_cache(cache)  # aioredis client
