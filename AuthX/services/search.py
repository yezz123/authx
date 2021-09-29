from typing import Optional

from fastapi import HTTPException

from AuthX.api import UsersRepo
from AuthX.models.user import UserPrivateInfo


class SearchService:
    _repo: UsersRepo

    @classmethod
    def setup(cls, repo: UsersRepo) -> None:
        """
        Setup the service with the given repository.
        """
        cls._repo = repo

    async def get_user(self, id: int):
        """
        Get a user by id.

        Args:
            id: The id of the user.

        Raises:
            HTTPException: If the user does not exist.

        Returns:
            The user.
        """
        item = await self._repo.get(id)
        if item is None:
            raise HTTPException(404)

        return UserPrivateInfo(**item).dict(by_alias=True)

    async def search(self, id: Optional[int], username: Optional[str], p: int) -> dict:
        """
        Search for users.

            Args:
                id: The id of the user.
                username: The username of the user.
                p: The page number.

            Returns:
                The users.
            """
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
