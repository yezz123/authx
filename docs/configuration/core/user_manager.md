# Testing

After taking a look at the configuration, you should now have a good idea of what you can do with the UserManager.

For example :

```py
async def get_by_login(self, login: str) -> Optional[dict]:
        try:
            valid_email = validate_email(login).email
            return await self.get_by_email(valid_email)
        except EmailNotValidError:
            return await self.get_by_username(login)
```

This one shows how we can use `GET` to fetch a user by login.

__Note__: All of this functions and configurations have a required file called config where we add all params for example :

- `Password_reset_lifetime`: How long a password reset token is valid.
- `Password_reset_max`: How many password reset tokens can be generated per user.

Also all of this is asynchronous with Redis and MongoDB, also we use a logger to set the log level and formatter.

## Testing

Let's try to test a `Usermanager` & creator based on this:

```py
import pytest

from AuthX.core.jwt import JWTBackend
from AuthX.core.user import User
from tests.utils import MockCacheBackend, private_key, public_key

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
```

This example show how we can create a user using a pre-configured JWTBackend and functionality based on the UserManager.

### MockCacheBackend

As we need we don't need to provide a Redis Service to the UserManager, we can use a MockCacheBackend to test the UserManager.

This class implements the CacheBackend interface, and is used to mock the Redis Service.

```py
class MockCacheBackend:
    def __init__(self) -> None:
        self._db = {}

    async def get(self, key: str) -> Optional[str]:
        return self._db.get(key)

    async def delete(self, key: str) -> None:
        try:
            self._db.pop(key)
        except KeyError:
            pass

    async def keys(self, match: str) -> Iterable[str]:
        return {}

    async def set(
        self, key: str,
        value: Union[str, bytes, int],
        expire: int) -> None:
        self._db[key] = value

    async def setnx(self, key: str,
        value: Union[str, bytes, int],
        expire: int) -> None:
        v = self._db.get(key)
        if v is None:
            self._db[key] = value

    async def incr(self, key: str) -> str:
        v = self._db.get(key)
        if v is not None:
            self._db[key] = int(v) + 1

    async def dispatch_action(self, channel: str,
        action: str, payload: str) -> None:
        print("Dispatching action")
        print(action)
        print(payload)
```
