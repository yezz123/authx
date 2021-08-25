from typing import Callable

from AuthX.api import UsersRepo
from AuthX.services import AdminService
from fastapi import APIRouter, Depends


def get_router(
    repo: UsersRepo, admin_required: Callable,
):

    AdminService.setup(repo)

    router = APIRouter()

    @router.get(
        "/blacklist", name="admin:get_blacklist", dependencies=[Depends(admin_required)]
    )
    async def get_blacklist():
        service = AdminService()
        return await service.get_blacklist()

    @router.post(
        "/{id}/blacklist",
        name="admin:toggle_blacklist",
        dependencies=[Depends(admin_required)],
    )
    async def toggle_blacklist(*, id: int):
        service = AdminService()
        return await service.toggle_blacklist(id)

    @router.get(
        "/blackout", name="admin:get_blackout", dependencies=[Depends(admin_required)]
    )
    async def get_blackout():
        service = AdminService()
        return await service.get_blackout()

    @router.post(
        "/blackout", name="admin:set_blackout", dependencies=[Depends(admin_required)]
    )
    async def set_blackout():
        service = AdminService()
        return await service.set_blackout()

    @router.delete(
        "/blackout",
        name="admin:delete_blackout",
        dependencies=[Depends(admin_required)],
    )
    async def delete_blackout():
        service = AdminService()
        return await service.delete_blackout()

    @router.get(
        "/id_by_username",
        name="admin:get_id_by_username",
        dependencies=[Depends(admin_required)],
    )
    async def get_id_by_username(*, username: str):
        service = AdminService()
        return await service.get_id_by_username(username)

    @router.post(
        "/{id}/kick", name="admin:kick", dependencies=[Depends(admin_required)]
    )
    async def kick(*, id: int):
        service = AdminService()
        return await service.kick(id)

    return router
