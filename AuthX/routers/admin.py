from typing import Callable

from fastapi import APIRouter, Depends

from AuthX.api import UsersRepo
from AuthX.services import AdminService


def get_router(
    repo: UsersRepo, admin_required: Callable,
):
    """
    Returns a router for the admin endpoints.

    Args:
        repo: The repository for the users.
        admin_required: A function that checks if the user is an admin.

    Returns:
        A router for the admin endpoints.
    """
    AdminService.setup(repo)

    router = APIRouter()
    """
    The router for the admin endpoints.

    Returns:
        The router for the admin endpoints.
    """

    @router.get(
        "/blacklist", name="admin:get_blacklist", dependencies=[Depends(admin_required)]
    )
    async def get_blacklist():
        """
        Returns the blacklist.

        Returns:
            The blacklist.
        """
        service = AdminService()
        return await service.get_blacklist()

    @router.post(
        "/{id}/blacklist",
        name="admin:toggle_blacklist",
        dependencies=[Depends(admin_required)],
    )
    async def toggle_blacklist(*, id: int):
        """
        Toggles the blacklist for the user.

        Args:
            id (int): The id of the user.

        Returns:
            The updated blacklist.
        """
        service = AdminService()
        return await service.toggle_blacklist(id)

    @router.get(
        "/blackout", name="admin:get_blackout", dependencies=[Depends(admin_required)]
    )
    async def get_blackout():
        """
        Returns the blackout.

        Returns:
            The blackout.
        """
        service = AdminService()
        return await service.get_blackout()

    @router.post(
        "/blackout", name="admin:set_blackout", dependencies=[Depends(admin_required)]
    )
    async def set_blackout():
        """
        Sets the blackout.

        Returns:
            The updated blackout.
        """
        service = AdminService()
        return await service.set_blackout()

    @router.delete(
        "/blackout",
        name="admin:delete_blackout",
        dependencies=[Depends(admin_required)],
    )
    async def delete_blackout():
        """
        Deletes the blackout.

        Returns:
            The updated blackout.
        """
        service = AdminService()
        return await service.delete_blackout()

    @router.get(
        "/id_by_username",
        name="admin:get_id_by_username",
        dependencies=[Depends(admin_required)],
    )
    async def get_id_by_username(*, username: str):
        """
        Returns the id of the user with the given username.

        Args:
            username (str): The username of the user.

        Returns:
            The id of the user with the given username.
        """
        service = AdminService()
        return await service.get_id_by_username(username)

    @router.post(
        "/{id}/kick", name="admin:kick", dependencies=[Depends(admin_required)]
    )
    async def kick(*, id: int):
        """
        Kicks the user with the given id.

        Args:
            id (int): The id of the user.

        Returns:
            The updated blacklist.
        """
        service = AdminService()
        return await service.kick(id)

    return router
