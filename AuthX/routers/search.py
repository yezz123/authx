from typing import Callable, Optional

from fastapi import APIRouter, Depends

from AuthX.api import UsersRepo
from AuthX.services import SearchService


def get_router(repo: UsersRepo, admin_required: Callable):

    SearchService.setup(repo)
    """
    Search router

    Returns:
        APIRouter -- Search router
    """

    router = APIRouter()

    @router.get("/{id}", name="auth:get_user", dependencies=[Depends(admin_required)])
    async def get_user(id: int):
        """
        Get user by id

        Args:
            id (int): User id

        Returns:
            dict -- User data
        """
        service = SearchService()
        return await service.get_user(id)

    @router.get("", name="auth:search", dependencies=[Depends(admin_required)])
    async def search(
        *, id: Optional[int] = None, username: Optional[str] = None, p: int = 1
    ):
        """
        Search users

        Args:
            id (Optional[int], optional): User id. Defaults to None.
            username (Optional[str], optional): User username. Defaults to None.
            p (int, optional): Page number. Defaults to 1.

        Returns:
            dict -- Users data
        """
        service = SearchService()
        return await service.search(id, username, p)

    return router
