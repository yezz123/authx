from datetime import datetime
from typing import Optional

from authx.backend.base import Base


class UsersManagementMixin(Base):
    """User Management MIXIN"""

    async def get_blacklist(self) -> dict:
        blacklist_db = await self._database.get_blacklist()  # pragma: no cover
        blacklist_cache = await self._cache.keys(
            "users:blacklist:*"
        )  # pragma: no cover
        blacklist_cache_ids = []  # pragma: no cover
        for key in blacklist_cache:  # pragma: no cover
            _, _, id = key.split(":")  # pragma: no cover
            blacklist_cache_ids.append(id)  # pragma: no cover
        return {
            "global": [
                {"id": item.get("id"), "username": item.get("username")}
                for item in blacklist_db
            ],
            "current": blacklist_cache_ids,
        }  # pragma: no cover

    async def toggle_blacklist(self, id: int) -> None:
        item = await self.get(id)  # pragma: no cover
        active = item.get("active")  # pragma: no cover
        await self.update(id, {"active": not active})  # pragma: no cover
        key = f"users:blacklist:{id}"  # pragma: no cover
        if active:  # pragma: no cover
            await self._cache.set(
                key, 1, expire=self._access_expiration
            )  # pragma: no cover
        else:  # pragma: no cover
            await self._cache.delete(key)  # pragma: no cover
        return None  # pragma: no cover

    async def kick(self, id: int) -> None:
        key = f"users:kick:{id}"  # pragma: no cover
        now = int(datetime.utcnow().timestamp())  # pragma: no cover

        await self._cache.set(
            key, now, expire=self._access_expiration
        )  # pragma: no cover

    async def get_blackout(self) -> Optional[str]:
        return await self._cache.get("users:blackout")  # pragma: no cover

    async def set_blackout(self, ts: int) -> None:
        await self._cache.set("users:blackout", ts)  # pragma: no cover

    async def delete_blackout(self) -> None:
        await self._cache.delete("users:blackout")  # pragma: no cover

    async def set_permissions(self) -> None:
        pass
