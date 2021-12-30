from typing import Optional

from fastapi import HTTPException

from authx.api import UsersRepo
from authx.models.user import UserPrivateInfo


class SearchService:
    """Class Search Service is a Class that contains all the methods to search for users, and get a user by id.
    Support Search by Page and Pagination for the users.
    """

    _repo: UsersRepo

    @classmethod
    def setup(cls, repo: UsersRepo) -> None:
        """Setup the service with the given repository."""
        cls._repo = repo

    async def get_user(self, id: int):
        """Get a user by id."""
        item = await self._repo.get(id)
        if item is None:
            raise HTTPException(404)

        return UserPrivateInfo(**item).dict(by_alias=True)

    async def search(self, id: Optional[int], username: Optional[str], p: int) -> dict:
        """Search for users."""
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
