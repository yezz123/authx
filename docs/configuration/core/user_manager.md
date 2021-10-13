# What's Next

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

This One Show how we can use GET to get a user by login.

__Note__: All of this Functions and Configurations have a one Require file called config where we add all parms for example :

- `Password_reset_lifetime`: How long a password reset token is valid.
- `Password_reset_max`: How many password reset tokens can be generated per user.

Also all of this is asynchronous with Redis & MongoDB, also we use a logger to set the log level & Formatter.

## Testing

Let's try to test a Usermanager & Creator based on this:

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

This Example show how we can create a user using a pre-configured JWTBackend and Functionality based on the UserManager.
