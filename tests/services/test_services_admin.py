import pytest
from fastapi.exceptions import HTTPException

from authx.api import UsersRepo
from authx.services import AdminService
from tests.utils import (
    MockAuthBackend,
    MockCacheBackend,
    MockDatabaseBackend,
    User,
    private_key,
    public_key,
)

admin = User(1, "admin", True)
user = User(2, "user", False)

auth_backend = MockAuthBackend("RS256", private_key, public_key)


@pytest.fixture(autouse=True)
def admin_service_setup():
    """
    Setup the admin service
    """
    AdminService.setup(
        UsersRepo(MockDatabaseBackend("test"), MockCacheBackend(), []),
    )


@pytest.mark.asyncio
async def test_get_blacklist():
    admin_service = AdminService()
    assert await admin_service.get_blacklist() == {}


@pytest.mark.asyncio
async def test_toggle_blacklist():
    admin_service = AdminService()
    await admin_service.toggle_blacklist(1)
    assert await admin_service.get_blacklist() == {1}


@pytest.mark.asyncio
async def test_get_blackout():
    admin_service = AdminService()
    assert await admin_service.get_blackout() == {"ts": "10.00"}


@pytest.mark.asyncio
async def test_set_blackout():
    admin_service = AdminService()
    await admin_service.set_blackout({"ts": "2020-01-01T00:00:00Z"})
    assert await admin_service.get_blackout() == {"ts": "10.00"}


@pytest.mark.asyncio
async def test_delete_blackout():
    admin_service = AdminService()
    await admin_service.set_blackout({"ts": "10.00"})
    await admin_service.delete_blackout()
    assert await admin_service.get_blackout() == {"ts": None}


@pytest.mark.asyncio
async def get_id_by_username():
    admin_service = AdminService()
    assert await admin_service.get_id_by_username("admin") == {"id": 1}


@pytest.mark.asyncio
async def get_permissions_by_username():
    admin_service = AdminService()
    assert await admin_service.get_permissions(1) == {}


@pytest.mark.asyncio
async def update_permissions():
    admin_service = AdminService()
    await admin_service.update_permissions(1, {"action": "ADD", "payload": "test"})
    assert await admin_service.get_permissions(1) == {"test": True}

    await admin_service.update_permissions(1, {"action": "REMOVE", "payload": "test"})
    assert await admin_service.get_permissions(1) == {}

    await admin_service.update_permissions(1, {"action": "CLEAR"})
    assert await admin_service.get_permissions(1) == {}

    with pytest.raises(HTTPException):
        await admin_service.update_permissions(1, {"action": "WRONG"})
