## Define your Base models

There are four Pydantic models variations provided as mixins:

* `UserInRegister` – User model for registering.
* `UserInCreate` – User model for creating.
* `UserInLogin` – User model for logging in.
* `UserInForgotPassword` – User model for forgot password.
* `UserPayload` – User model for payloads.
* `UserInSetPassword` – User model for setting password.
* `UserInChangePassword` – User model for changing password.
* `UserInChangeUsername` – User model for changing username.
* `UserPrivateInfo` – User model for private info.

You should define each of those variations, inheriting from each mixin:

```py
from AuthX.models import user


class register(user.UserInRegister):
    pass


class Create(user.UserInCreate):
    pass


class login(user.UserInLogin):
    pass


class private(user.UserPrivateInfo):
    pass
```

### Adding your own fields

You can of course add your own properties there to fit to your needs. In the example below, we add a required string property, `first_name`, and an optional string property, `phone`.

```py
from AuthX.models import user


class register(user.UserInRegister):
    first_name: str
    phone: str


class login(user.UserInLogin):
    first_name: str
    phone: str


class UserUpdate(user.UserInChangeUsername):
    first_name: str
    phone: str

```

Check the [pydantic documentation](https://pydantic-docs.helpmanual.io/usage/models/) for more information.

Check also:

* [Social Models](social.md)
* [Properties](properties.md)
