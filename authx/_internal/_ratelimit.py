"""Rate limiting utilities for AuthX."""

import time
from typing import Any, Callable, Optional, Protocol, Union

from fastapi import Request


class RateLimitBackend(Protocol):
    """Protocol for rate limit storage backends."""

    async def increment(self, key: str, window: int) -> int:
        """Increment the counter for a key and return the new count.

        Args:
            key: The rate limit key (e.g. client IP).
            window: Time window in seconds.

        Returns:
            The current request count within the window.
        """
        ...

    async def reset(self, key: str) -> None:
        """Reset the counter for a key."""
        ...


class InMemoryBackend:
    """In-memory rate limit backend using a simple dict.

    Suitable for single-process deployments. For multi-worker setups,
    implement ``RateLimitBackend`` with Redis or another shared store.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[int, float]] = {}

    async def increment(self, key: str, window: int) -> int:
        now = time.monotonic()
        entry = self._store.get(key)
        if entry is None or now - entry[1] >= window:
            self._store[key] = (1, now)
            return 1
        count = entry[0] + 1
        self._store[key] = (count, entry[1])
        return count

    async def reset(self, key: str) -> None:
        self._store.pop(key, None)

    def _cleanup(self, window: int) -> None:
        """Remove expired entries. Call periodically if memory is a concern."""
        now = time.monotonic()
        expired = [k for k, (_, ts) in self._store.items() if now - ts >= window]
        for k in expired:
            del self._store[k]


def _default_key_func(request: Request) -> str:
    """Extract client IP from request as the default rate limit key."""
    if request.client is not None:
        return f"ratelimit:{request.client.host}"
    return "ratelimit:unknown"


class RateLimiter:
    """A FastAPI-compatible rate limiter dependency.

    Usage::

        limiter = RateLimiter(max_requests=10, window=60)

        @app.get("/api", dependencies=[Depends(limiter)])
        async def api_route():
            ...
    """

    def __init__(
        self,
        max_requests: int = 10,
        window: int = 60,
        backend: Optional[Any] = None,
        key_func: Optional[Callable[[Request], Union[str, Any]]] = None,
    ) -> None:
        """Initialize the rate limiter.

        Args:
            max_requests: Maximum number of requests allowed within the window.
            window: Time window in seconds.
            backend: Storage backend implementing ``RateLimitBackend``. Defaults to ``InMemoryBackend``.
            key_func: Callable that extracts a key from the request. Defaults to client IP.
        """
        self.max_requests = max_requests
        self.window = window
        self.backend: Any = backend or InMemoryBackend()
        self.key_func = key_func or _default_key_func

    async def __call__(self, request: Request) -> None:
        """FastAPI dependency entrypoint. Raises ``RateLimitExceeded`` when the limit is breached."""
        from authx.exceptions import RateLimitExceeded

        key = self.key_func(request)
        count = await self.backend.increment(key, self.window)
        if count > self.max_requests:
            raise RateLimitExceeded(retry_after=self.window)
