# Models

**AuthX** defines a minimal User model for authentication purposes. It is structured like this:

* `id` (`int`) – Unique identifier of the user. Defaults to a **Int**.
* `email` (`str`) – Email of the user. Validated by [`email-validator`](https://github.com/JoshData/python-email-validator).
* `active` (`bool`) – Whether or not the user is active. If not, login and forgot password requests will be denied. Defaults to `True`.
* `confirmed` (`bool`) – Whether or not the user is verified. Optional but helpful with the `verify` router logic. Defaults to `False`.
* `permissions` (`bool`) – Whether or not the user is a superuser. Useful to implement administration logic. Defaults to `False`.
* `last_login` (`datetime`) – When the user last logged in. Defaults to `None`.
* `created_at` (`datetime`) – When the user was created. Defaults to `None`.

There is also a Social User model that is a class of the AuthX User model.

* `provider` (`str`) – The provider of the social user.
* `sid` (`str`) – The unique identifier of the social user.
* `active` (`bool`) – Whether or not the social user is active. Defaults to `True`.
* `confirmed` (`bool`) – Not like Base Case,but when a user logs in with a social user, the social user is confirmed. Defaults to `True`.

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

## Define your Social Models

There are one Pydantic model variation provided as mixin:

* `SocialInCreate` – Social User model for creating.

You should define it, inheriting from the mixin:

```py
from AuthX.models import social

class Create(social.SocialInCreate):
    pass
```

## Properties

There is a file `common.py` that contains the common properties for all models.

`set_created_at` (`bool`) – Return the created_at property as a datetime object.

`set_last_login` (`bool`) – Return the last_login property as a datetime object.

Also a Class `DefaultModel` that can be used to define a default model, with a Configuration that allow:

* `allow_population_by_field_name` – Allow population by field name. default: `True`.
* `alias_generator` – this one based on a Function, called `convert_field_to_camel_case` that converts a field name to a camel case. default: `None`.
