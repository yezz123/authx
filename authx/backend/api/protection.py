from authx.backend.base import Base
from authx.core.config import LOGIN_RATELIMIT
from authx.core.logger import logger


class UsersProtectionMixin(Base):
    """User Protection MIXIN"""

    async def _check_timeout_and_incr(self, key: str, max: int, timeout: int) -> bool:
        """
        Check if the timeout is expired and increment the counter.
        """
        count = await self._cache.get(key)
        if count is not None:
            count = int(count)  # pragma: no cover
            if count >= max:  # pragma: no cover
                return False  # pragma: no cover
            await self._cache.incr(key)  # pragma: no cover
        else:
            await self._cache.set(key, 1, expire=timeout)

        return True

    async def is_bruteforce(self, ip: str, login: str) -> bool:
        """
        Check if the ip is in the bruteforce list.
        """
        timeout_key = f"users:login:timeout:{ip}"
        timeout = await self._cache.get(timeout_key)

        if timeout is not None:
            return True  # pragma: no cover

        rate_key = f"users:login:rate:{ip}"
        rate = await self._cache.get(rate_key)

        if rate is not None:
            rate = int(rate)  # pragma: no cover
            if rate > LOGIN_RATELIMIT:  # pragma: no cover
                await self._cache.set(timeout_key, 1, expire=60)  # pragma: no cover
                logger.info(
                    f"bruteforce_login ip={ip} login={login}"
                )  # pragma: no cover
                return True  # pragma: no cover
        else:
            await self._cache.set(rate_key, 1, expire=60)

        await self._cache.incr(rate_key)
        return False
