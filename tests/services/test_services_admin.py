import pytest

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
async def test_get_blacklist(admin_service_setup):
    blacklist = await admin_service_setup.get_blacklist()
    assert blacklist == []


@pytest.mark.asyncio
async def test_toggle_blacklist(admin_service_setup):
    await admin_service_setup.toggle_blacklist(1)
    blacklist = await admin_service_setup.get_blacklist()
    assert blacklist == [1]


@pytest.mark.asyncio
async def test_get_blackout(admin_service_setup):
    ts = await admin_service_setup.get_blackout()
    assert ts is None


@pytest.mark.asyncio
async def test_set_blackout(admin_service_setup):
    await admin_service_setup.set_blackout(1)
    ts = await admin_service_setup.get_blackout()
    assert ts == 1


@pytest.mark.asyncio
async def test_delete_blackout(admin_service_setup):
    await admin_service_setup.set_blackout(1)
    await admin_service_setup.delete_blackout()
    ts = await admin_service_setup.get_blackout()
    assert ts is None


@pytest.mark.asyncio
async def get_id_by_username(admin_service_setup):
    id = await admin_service_setup.get_id_by_username("admin")
    assert id == 1


@pytest.mark.asyncio
async def get_permissions_by_username(admin_service_setup):
    permissions = await admin_service_setup.get_permissions_by_username("admin")
    assert permissions == ["admin"]


@pytest.mark.asyncio
async def update_permissions(admin_service_setup):
    await admin_service_setup.update_permissions("admin", ["admin", "user"])
    permissions = await admin_service_setup.get_permissions_by_username("admin")
    assert permissions == ["admin", "user"]
