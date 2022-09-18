# Password Router

The password router is a router use to provide different state of passwords, for
example forget password, reset password, etc.

- POST `/forgot_password`
- GET `/password`
- POST `password`
- POST `/password/{token}`
- PUT `/password`

## Setup the Password Service

To Setup the Password service, you will need to add all requirements to the
object `PasswordService`:

```py
from authx.services.password import PasswordService
from authx.api import UsersRepo
from authx.core.jwt import JWTBackend

PasswordService.setup(
        repo = UsersRepo,
        auth_backend = JWTBackend,
        debug = True,
        base_url= "http://localhost:8000",
        site= "http://localhost:8000",
        recaptcha_secret = None,
        smtp_username= None,
        smtp_password= None,
        smtp_host= None,
        smtp_tls= None,
        display_name= "authx",
    )
```

This one gonna help use to use the Password service, that we provide.

```py
from authx import Authentication
from fastapi import FastAPI

app = FastAPI()
auth = Authentication()

app.include_router(auth.password_router, prefix="/api/users")
```

### Forgot Password

This is a `POST` request to `/forgot_password` that will send a request getting
the Data(Login, Password) and IP address of the user, this one work only for
accounts with a pre-configured password.

```py
@router.post("/forgot_password", name="auth:forgot_password")
    async def forgot_password(*, request: Request):
        data = await request.json()
        ip = request.client.host
        service = PasswordService()
        return await service.forgot_password(data, ip)
```

Now lets try to understand the concept that we have in
`service.forgot_password`:

- This one return a `Response` object, that we can use to send a response to the
  user.
- If the user is not found, we will raise an HTTPException with the status code
  404, we could get also `400` if the data is not valid or time is expired.

```py
async def forgot_password(self, data: dict, ip: str) -> None:
        try:
            email = UserInForgotPassword(**data).email
        except ValidationError:
            raise HTTPException(400, detail=get_error_message("validation"))

        item = await self._repo.get_by_email(email)

        if item is None:
            raise HTTPException(404, detail=get_error_message("email not found"))

        if item.get("password") is None:
            raise HTTPException(406)

        id = item.get("id")

        if not await self._repo.is_password_reset_available(id):
            raise HTTPException(400, detail=get_error_message("reset before"))
        logger.info(f"forgot_password ip={ip} email={email}")

        token = create_random_string()
        token_hash = hash_string(token)

        await self._repo.set_password_reset_token(id, token_hash)

        email_client = self._create_email_client()
        await email_client.send_forgot_password_email(email, token)

        return None
```

### Password Status

Using a `GET` Method to get the status of the password, based on the logged
user.

```py
@router.get("/password", name="auth:password_status")
    async def password_status(*, user: User = Depends(get_authenticated_user)):
        service = PasswordService(user)
        return await service.password_status()
```

This one gonna return a dict where the response gonna show up the status of the
password.

`Service.password_status` will return a dict with the following keys:

```py
async def password_status(self) -> dict:
        status = await self._repo.get_password_status(self._user.id)
        return {"status": status}
```

This one also relate to the `UsersPasswordMixin` Class.

### Password Set

To Set a Password that require a `POST` request to `/password` that will send a
request with the token and the new password, here we use as a parameter the
request where we have the token and also the Authenticated User (Optional for
Admins).

```py
@router.post("/password", name="auth:password_set")
    async def password_set(
        *, request: Request,
        user: User = Depends(get_authenticated_user)
    ):
        data = await request.json()
        service = PasswordService(user)
        return await service.password_set(data)
```

As always we use a Pre-configured Services (`Service.password_set`) where we
have 2 ways to set the password.

- First Example:

```py
async def password_set(self, data: dict) -> None:
        item = await self._repo.get(self._user.id)
        return {
            "password": item.get("password") is not None,
            "provider": item.get("provider") is not None,
            "reset_available": await self._repo.is_password_reset_available(
                self._user.id
            ),
        }
```

- Second Example:

```py
async def password_set(self, data: dict) -> None:
        item = await self._repo.get(self._user.id)
        if item.get("provider") is not None and item.get("password") is None:
            user_model = self._validate_user_model(UserInSetPassword, data)
            password_hash = get_password_hash(user_model.password1)
            await self._repo.set_password(self._user.id, password_hash)
            return None
        else:
            raise HTTPException(400, get_error_message("password already exists"))
```

Both of them gonna return a `Response` object, that we can use to send a
response to the user.

### Password Reset

Reset the password using a `POST` request to `/password/{token}` that will send
a request with the new password, here we use as a parameter the request and a
string token.

```py
@router.post(
    "/password/{token}",
    name="auth:password_reset")
    async def password_reset(*, token: str, request: Request):
        data = await request.json()
        service = PasswordService()
        return await service.password_reset(data, token)
```

To reset the password we pass data under this format:

```json
data: {password1: "password", password2: "password"}
```

with the token that we have in the `forgot_password` request, to validate and
reset the password.

```py
async def password_reset(self, data: dict, token: str) -> None:
        token_hash = hash_string(token)

        id = await self._repo.get_id_for_password_reset(token_hash)
        if id is None:
            raise HTTPException(404)

        user_model = self._validate_user_model(UserInSetPassword, data)

        password_hash = get_password_hash(user_model.password1)
        await self._repo.set_password(id, password_hash)

        return None
```

!!! Warning

        You could get the HTTPException if:

            * `404` : The token is not found.
            * `400` : Token Validation Error.

### Password Change

After Passing all this steps, Now we can use `PUT` to change the password of the
user, this one will send a request with the new password, here we use as a
parameter the request and User (Defaults to Depends `get_authenticated_user`).

```py
@router.put("/password", name="auth:password_change")
    async def password_change(
        *, request: Request, user: User = Depends(get_authenticated_user)
    ):
        data = await request.json()
        service = PasswordService(user)
        return await service.password_change(data)

    return router
```

Equivalent to `password_set` but with the `PUT` request, we pass the data under
the same format.

```py
async def password_change(self, data: dict) -> None:
        user_model = self._validate_user_model(UserInChangePassword, data)
        item = await self._repo.get(self._user.id)

        if not verify_password(user_model.old_password, item.get("password")):
            raise HTTPException(400, detail=get_error_message("password invalid"))

        password_hash = get_password_hash(user_model.password1)
        await self._repo.set_password(self._user.id, password_hash)
        return None
```

!!! Warning

        You could get the HTTPException if:

            * `404` : The token is not found.
            * `400` : Token Validation Error.
