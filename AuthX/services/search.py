from typing import Optional

from fastapi import HTTPException

from AuthX.api import UsersRepo
from AuthX.models.user import UserPrivateInfo


class SearchService:
    _repo: UsersRepo

    @classmethod
    def setup(cls, repo: UsersRepo) -> None:
        cls._repo = repo

    async def get_user(self, id: int):
        item = await self._repo.get(id)
        if item is None:
            raise HTTPException(404)

        return UserPrivateInfo(**item).dict(by_alias=True)

    async def search(self, id: Optional[int], username: Optional[str], p: int) -> dict:
        PAGE_SIZE = 20
        items, count = await self._repo.search(id, username, p, PAGE_SIZE)
        div = count // PAGE_SIZE
        pages = div if count % PAGE_SIZE == 0 else div + 1
        return {
            "items": [
                UserPrivateInfo(**item).dict(by_alias=True, exclude_none=True)
                for item in items
            ],
            "pages": pages,
            "currentPage": p,
        }
