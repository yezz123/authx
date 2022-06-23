# Authentication Router

The auth router will generate a set of endpoints for authenticating users.

- POST `/register`
- POST `/login`
- POST `/logout`
- POST `/token`
- POST `/token/refresh`
- GET `/confirm`
- POST `/confirm`
- POST `/confirm/{token}`
- POST `/{id}/change_username`

## Setup The Authentication service

To Setup the authentication service, you will need to add all requirements to
the object `AuthService`.

```py
from authx.services.auth import AuthService
from authx.api import UsersRepo
from authx.core.jwt import JWTBackend

AuthService.setup(
        repo = UsersRepo,
        auth_backend = JWTBackend,
        debug = True,
        base_url = 'http://localhost:8000',
        site = 'authx',
        recaptcha_secret = None,
        smtp_username = None,
        smtp_password = None,
        smtp_host = None,
        smtp_tls = False,
        display_name = 'authx',
    )
```

This one gonna help use to use the authentication service, that we provide.

```py
from authx import Authentication
from fastapi import FastAPI

app = FastAPI()
auth = Authentication()

app.include_router(auth.auth_router, prefix="/api/users")
```

### Register

As we know we will use the `POST` method to register a new user, also a callback
method.

This Route is based on:

```py
@router.post("/register", name="auth:register")
    async def register(*, request: Request, response: Response):
        data = await request.json()
        service = AuthService()

        tokens = await service.register(data)
        set_tokens_in_response(response, tokens)
        return None
```

The `Service.register` method will return the Access and Refresh tokens, and if
we have a validation error it will return the error `400`.

### Login

Same logical way as [register](#register), we use the same Authentication route.

!!! info `app.include_router(auth.auth_router, prefix="/api/users")` include all
authentication routers.

```py
@router.post("/login", name="auth:login")
    async def login(*, request: Request, response: Response):
        data = await request.json()
        service = AuthService()
        ip = request.client.host
        tokens = await service.login(data, ip)
        set_tokens_in_response(response, tokens)
        return None
```

For the `login` Service we provide some params:

- `data`: The data that we will use to login. (login, password).
- `ip`: The IP of the client.

if the `data` is not valid, we will return the error `400`, if the `data` is
valid, we will return the tokens (access and refresh).

!!! info There is also an `HTTPException` relate to `404` if the user is not
found, also the `429` relate to brute force attempts.

!!! info The HTTP `429` Too Many Requests response status code indicates the
user has sent too many requests in a given amount of time ("rate limiting"). A
Retry-After header might be included to this response indicating how long to
wait before making a new request.

### Logout

As we know `logout` always mean that we will remove the `access_cookies_name`
and `refresh_cookies_name` from the response.

```py
@router.post("/logout", name="auth:logout")
    async def logout(*, response: Response):
        response.delete_cookie(access_cookie_name)
        response.delete_cookie(refresh_cookie_name)
        return None
```

The `response.delete_cookie` is a function in the `starlette` a lightweight ASGI
framework/toolkit, which is ideal for building high performance asyncio
services.

### Token

After login and all the steps we have a function relate to get a new token based
on `user` a class that initalize the user object and use `data` (login,
password) as an argument.

```py
@router.post("/token", name="auth:token")
    async def token(*, user: User = Depends(get_authenticated_user)):
        return user.data
```

- User Data:

```py
def __init__(self, data=None):
        self.data = data
        if data is None:
            self.is_authenticated = False
            self.is_admin = False
            self.id = None
            self.username = None
        else:
            self.is_authenticated = True
            self.is_admin = "admin" in self.data.get("permissions")
            self.id = int(self.data.get("id"))
            self.username = self.data.get("username")
```

#### Refresh Token

We have also a way to get a new refresh token, this is the same as the `token`
method, but we will use the `refresh_token` instead of `access_token`, it take
`request` & `response` as arguments, use also `starlette` to set the
`refresh_cookie_name` in the response.

```py
@router.post("/token/refresh", name="auth:refresh_access_token")
    async def refresh_access_token(
        *, request: Request, response: Response,
    ):
        service = AuthService()
        refresh_token = request.cookies.get(refresh_cookie_name)
        if refresh_token is None:
            raise HTTPException(401)

        access_token = await service.refresh_access_token(refresh_token)
        set_access_token_in_response(response, access_token)
        return {"access": access_token}
```

- The `service.refresh_access_token` will return the new access token, or it
  will raise;
  - `401`: if the refresh token is not valid. (Refresh or Ban).
  - `500`: if the refresh token is expired.

!!! info `set_access_token_in_response` take the `response` and the `token` as
arguments, also set :
`py response.set_cookie( key=refresh_cookie_name, value=token, secure=not debug, httponly=True, max_age=refresh_expiration, ) `

### Confirm

We have 3 steps for the Email confirmation:

- [get_email_confirmation_status](#ConfirmationStatus)
- [request_email_confirmation](#RequestConfirmation)
- [confirm_email](#Confirmation)

#### ConfirmationStatus

For the `get_email_confirmation_status` we will use the `GET` method, and we
will return the status of the email confirmation.

```py
@router.get("/confirm", name="auth:get_email_confirmation_status")
    async def get_email_confirmation_status(
        *, user: User = Depends(get_authenticated_user)
    ):
        service = AuthService(user)
        return await service.get_email_confirmation_status()
```

The `service.get_email_confirmation_status()` gonna return the status of the
email confirmation. `{"email": sample@sample.com, "confirmed": True}`

```py
async def get_email_confirmation_status(self) -> dict:
        item = await self._repo.get(self._user.id)
        return {"email": item.get("email"), "confirmed": item.get("confirmed")}
```

#### RequestConfirmation

for the `request_email_confirmation` we will use the `POST` method, and we will
return the status of the email confirmation, its take the `user` as an arguments
or by default its depend on `get_authenticated_user`.

```py
@router.post("/confirm", name="auth:request_email_confirmation")
    async def request_email_confirmation(
        *, user: User = Depends(get_authenticated_user)):
        service = AuthService(user)
        return await service.request_email_confirmation()
```

the `service.request_email_confirmation()` check the email if is confirmed or
not, for example if is not confirmed its return a link to confirm this email, if
confirmed raise an HTTPException `400` with the message
`Email already confirmed`, also can show the timeout exception.

```py
async def request_email_confirmation(self) -> None:
        item = await self._repo.get(self._user.id)
        if item.get("confirmed"):
            raise HTTPException(400)
        if not await self._repo.is_email_confirmation_available(self._user.id):
            raise HTTPException(429)
        email = item.get("email")
        await self._request_email_confirmation(email)
        return None
```

#### Confirmation

For the `confirm_email` function we will use the `POST` method, and it will
return a response with a token to verify, its take the `token` as an arguments.

```py
@router.post("/confirm/{token}", name="auth:confirm_email")
    async def confirm_email(*, token: str):
        service = AuthService()
        return await service.confirm_email(token)
```

The `service.confirm_email` hash the token, or looks up hash in db to update the
confirmed row to row (Default is `false`), this could raise also `403` an
HTTPException that show if there is no hash in database.

```py
async def confirm_email(self, token: str) -> None:
        token_hash = hash_string(token)
        if not await self._repo.confirm_email(token_hash):
            raise HTTPException(403)
        return None
```

### Change Username

At the last point of authentication we have a function to change the username,
it take `id`, `username`, `user` as arguments, and return a response with the
new username.

```py
@router.post("/{id}/change_username", name="auth:change_username")
    async def change_username(
        *,
        id: int,
        username: str = Body("", embed=True),
        user: User = Depends(get_authenticated_user),):
        service = AuthService(user)
        if user.id == id or user.is_admin:
            return await service.change_username(id, username)
        else:
            raise HTTPException(403)
    return router
```

The `service.change_username` will return the new username, or it will raise; -
`400`: Username already exists. - `404`: user not found.

```py
async def change_username(self, id: int, username: str) -> None:
        new_username = self._validate_user_model(
            UserInChangeUsername, {"username": username}
        ).username
        item = await self._repo.get(id)
        old_username = item.get("username")
        if old_username == new_username:
            raise HTTPException(400, detail=get_error_message("username change same"))
        existing_user = await self._repo.get_by_username(new_username)
        if existing_user is not None:
            raise HTTPException(400, detail=get_error_message("existing username"))
        logger.info(
            f"change_username id={id} old_username={old_username} new_username={new_username}"
        )
        await self._repo.change_username(id, new_username)
        logger.info(f"change_username id={id} success")
        return None
```
