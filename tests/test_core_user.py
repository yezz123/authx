import pytest

from AuthX.core.jwt import JWTBackend
from AuthX.core.user import User

from .utils import MockCacheBackend, private_key, public_key

jwt_backend = JWTBackend(MockCacheBackend(), private_key, public_key, 60, 60 * 10)
ID = 1
USERNAME = "admin"
PERMISSIONS = ["admin"]

sample_access_token = jwt_backend.create_access_token(
    {"id": ID, "username": USERNAME, "permissions": PERMISSIONS}
)


@pytest.mark.asyncio
async def test_user():
    user = await User.create(sample_access_token, jwt_backend)
    assert user.is_authenticated
    assert user.id == ID
    assert user.username == USERNAME
    assert user.is_admin


@pytest.mark.asyncio
async def test_anonim_user():
    anonim_user = await User.create(None, jwt_backend)
    assert not anonim_user.is_authenticated
    assert anonim_user.id is None
    assert anonim_user.username is None
    assert not anonim_user.is_admin
