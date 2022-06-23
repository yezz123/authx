from typing import Optional

from authx.backend.base import Base
from authx.core.config import (
    PASSWORD_RESET_LIFETIME,
    PASSWORD_RESET_MAX,
    PASSWORD_RESET_TIMEOUT,
)


class UsersPasswordMixin(Base):
    """User Password MIXIN"""

    async def get_password_status(self, id: int) -> str:
        item = await self.get(id)
        if item.get("provider") is not None and item.get("password") is None:
            return "set"  # pragma: no cover
        else:
            return "change"

    async def set_password(self, id: int, password: str) -> None:
        await self.update(id, {"password": password})

    async def is_password_reset_available(self, id: int) -> bool:
        key = f"users:reset:count:{id}"
        return await self._check_timeout_and_incr(
            key, PASSWORD_RESET_MAX, PASSWORD_RESET_TIMEOUT
        )  # type: ignore

    async def set_password_reset_token(self, id: int, token_hash: str) -> None:
        key = f"users:reset:token:{token_hash}"
        await self._cache.set(key, id, expire=PASSWORD_RESET_LIFETIME)

    async def get_id_for_password_reset(self, token_hash: str) -> Optional[int]:
        id = await self._cache.get(f"users:reset:token:{token_hash}")
        return int(id) if id is not None else None
