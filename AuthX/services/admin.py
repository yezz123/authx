from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from AuthX.api import UsersRepo


class AdminService:
    """ Create the Admin Service

    Raises:
        HTTPException: if the service could not be created properly (e.g. if the database could not be accessed)

        HTTPException: if the service could not be created because the repo could not be created properly (e.g. if the database could not be accessed)

    Returns:
        AdminService: the created service
    """

    _repo: UsersRepo

    @classmethod
    def setup(cls, repo: UsersRepo) -> None:
        cls._repo = repo

    async def get_blacklist(self) -> dict:
        return await self._repo.get_blacklist()

    async def toggle_blacklist(self, id: int) -> None:
        return await self._repo.toggle_blacklist(id)

    async def get_blackout(self) -> dict:
        ts = await self._repo.get_blackout()
        if ts is None:
            raise HTTPException(404)

        ts = datetime.utcfromtimestamp(int(ts))  # type: ignore
        return {"ts": ts.strftime("%d.%m.%Y, %H:%M UTC")}  # type: ignore

    async def set_blackout(self) -> None:
        epoch = datetime.utcfromtimestamp(0)
        ts = int((datetime.utcnow() - epoch).total_seconds()) + 10
        await self._repo.set_blackout(ts)
        return None

    async def delete_blackout(self) -> None:
        await self._repo.delete_blackout()

    async def get_id_by_username(self, username: str) -> Optional[dict]:
        item = await self._repo.get_by_username(username)
        return {"id": item.get("id")}

    async def get_permissions(self, id: int) -> dict:
        return {}

    async def update_permissions(self, id: int, data: dict) -> None:
        action = data.get("action")
        payload = data.get("payload")

        item = await self._repo.get(id)
        permissions = item.get("permissions")

        if action == "ADD":
            permissions.append(payload)
            await self._repo.update(id, {"permissions": list(set(permissions))})
        elif action == "REMOVE":
            permissions.remove(payload)
            await self._repo.update(id, {"permissions": permissions})

        elif action == "CLEAR":
            await self._repo.update(id, {"permissions": []})

        else:
            raise HTTPException(400, detail="wrong action")

        await self.kick(id)

        return None

    async def kick(self, id: int) -> None:
        await self._repo.kick(id)
