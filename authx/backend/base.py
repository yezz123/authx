from typing import Iterable, Optional

from authx.cache import RedisBackend
from authx.database import BaseDBBackend


class Base:
    """Initialize the API with the database and cache."""

    def __init__(
        self,
        database: BaseDBBackend,
        cache: RedisBackend,
        callbacks: Iterable,
        access_expiration: int = 60**2 * 6,
    ):
        self._database: Optional[BaseDBBackend] = database
        self._cache: Optional[RedisBackend] = cache
        self._callbacks = callbacks
        self._access_expiration = access_expiration
