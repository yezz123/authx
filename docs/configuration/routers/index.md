# Routers

We're almost there! The last step is to configure the `authx` object that will
wire the user manager, the authentication classes and let us generate the actual
**API routes**.

## Configure `authx`

Configure `authx` object with all the elements we defined before. More
precisely:

- `UserManager`: Dependency callable getter to inject the user manager class
  instance. See [UserManager](../core/index.md).
- `auth_backends`: List of authentication backends. See
  [Authentication](../auth/index.md).
- `user_model`: Pydantic model of a user.
- `UserInRegister` – User model for registering.
- `UserInCreate` – User model for creating.
- `UserInLogin` – User model for logging in.
- `UserPayload` – User model for payloads.
- `SocialInCreate` – Social User model for creating.

```py
from authx import Authentication

Authentication = Authentication(
    debug=True,
    base_url="http://localhost:8000",
    site="http://localhost:8000",
    database_name="authx",
    callback_url="http://localhost:8000/callback",
    access_cookie_name="access_token",
    refresh_cookie_name="refresh_token",
    private_key="private.pem",
    public_key="public.pem",
    access_expiration=3600,
    refresh_expiration=86400,
    smtp_username=None,
    smtp_host=None,
    smtp_password=None,
    smtp_tls=False,
    display_name="authx",
    recaptcha_secret=None,
    social_creds=None,
    social_providers=None,
)
```

**Note:** We gonna discuss what we define in `Authentication` Next.

!!! info We Have also an other configuration option, `authx` and `User`.

## Available routers

This helper class will let you generate useful routers to setup the
authentication system. Each of them is **optional**, so you can pick only the
one that you are interested in! Here are the routers provided:

- [Authentication](authentication.md): Provides `/login` and `/logout` also
  `/register` and some other useful endpoints based on
  [Authentication Provider](../auth/index.md).
- [Administration](.administration.md): Provides all the services that an Admin
  can use to manage the users. (`/blacklist`, `/blackout`, `kick`)
- [Password](password.md): Provides `/forgot` and `/reset` and `/set` endpoints
  to reset the password.
- [social](social.md): Provides `/social` and `/social/callback` endpoints to
  login with social networks, relate to [Social Provider](../social/index.md).
- [Search](search.md): Provides `/search` endpoint to search users.

You should check out each of them to understand how to use them.
