# Social Router

The Social router will generate a set of endpoints for
[Social Authentication](../social/index.md) users.

- GET `/{provider}`
- GET `/{provider}/callback`

## Setup the Social Router

To Setup the Social authentication service, you will need to add all
requirements to the object `SocialService`.

```py
from authx.services import SocialService
from authx.api import UsersRepo
from authx.core.jwt import JWTBackend

SocialService.setup(
        repo = UserRepo,
        auth_backend = JWTBackend,
        base_url = 'http://localhost:8000',
        option = 'social',
    )
```

This one gonna help use to use the authentication service, that we provide.

```py
from authx import Authentication
from fastapi import FastAPI

app = FastAPI()
auth = Authentication()

app.include_router(auth.social_router, prefix="/auth")
```

!!! info

        We describe the `SocialService` object in the
        [Social Service](../social/index.md) documentation.

### Login

Using `GET` Method to login, after provide all parameters like the `provider`
(ex. Facebook,Google,etc), `request`, all of that gonna return a
`RedirectResponse where we gonna redirect the user to the provider.

```py
@router.get("/{provider}", name="social:login")
    async def login(*, provider: str, request: Request):
        check_provider(provider)
        service = SocialService()
        method = getattr(service, f"login_{provider}")

        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        request.session["state"] = state

        redirect_uri = method(state)
        return RedirectResponse(redirect_uri)
```

Before, send the request to the provider, we gonna check if the provider is
valid.

```py
def check_provider(provider):
        if provider not in social_providers:
            raise HTTPException(404)
```

!!! info

        Until Now AuthX Support the following providers:

            * Facebook : [Read More](../social/facebook.md)
            * Google : [Read More](../social/google.md)

After checking the Provider, we gonna check if the SocialService is setup, and
then the method `login_{provider}` is available.

### Callback

Same as the `login` method, the Callback is based on `GET` method, with the same
Arguments, but with a different return, cause here we gonna return an
`HTMLResponse` that gonna redirect the user to the home page.

As always, we gonna check first if the `provider` is valid, and then we gonna
check if the `state` is valid.

```py
@router.get("/{provider}/callback", name="social:callback")
    async def callback(*, provider: str, request: Request):
        check_provider(provider)

        state_query = request.query_params.get("state")
        state_session = request.session.get("state")

        if not check_state(state_query, state_session):
            raise HTTPException(403)
```

!!! Warning

        if The stale is not valid we gonna raise an HTTPException with a
        status code of 403.

Now we gonna Create `code` where we gonna get a `query_params` with the `code`
from the provider, without forgetting the `SocialService`, and the Method where
we gonna callback the provider.

```py
code = request.query_params.get("code")
service = SocialService()
method = getattr(service, f"callback_{provider}")

sid, email = await method(code)
```

Now, lets try to create the token and redirect the user to the home page, the
response use `set_cookie` to set the token in the cookie.

```py
response.set_cookie(
    key=access_cookie_name,
    value=tokens.get("access"),
    secure=not debug,
    httponly=True,
    max_age=access_expiration,
)
response.set_cookie(
    key=refresh_cookie_name,
    value=tokens.get("refresh"),
    secure=not debug,
    httponly=True,
    max_age=refresh_expiration,
)
```

Now if the user is not logged in, we gonna redirect a `SocialException` as an
`HTMLReponse` with a `status_code`.

```py
    return response
except SocialException as e:
    return HTMLResponse(e.content, status_code=e.status_code)
```

#### Full Callback

```py
@router.get("/{provider}/callback", name="social:callback")
    async def callback(*, provider: str, request: Request):
        check_provider(provider)

        state_query = request.query_params.get("state")
        state_session = request.session.get("state")

        if not check_state(state_query, state_session):
            raise HTTPException(403)
        code = request.query_params.get("code")
        service = SocialService()
        method = getattr(service, f"callback_{provider}")

        sid, email = await method(code)

        try:
            tokens = await service.resolve_user(provider, sid, email)
            response = RedirectResponse("/")
            response.set_cookie(
                key=access_cookie_name,
                value=tokens.get("access"),
                secure=not debug,
                httponly=True,
                max_age=access_expiration,
            )
            response.set_cookie(
                key=refresh_cookie_name,
                value=tokens.get("refresh"),
                secure=not debug,
                httponly=True,
                max_age=refresh_expiration,
            )
            return response
        except SocialException as e:
            return HTMLResponse(e.content, status_code=e.status_code)

    return router
```

!!! Info

        Also, an [Addons](../social/addons.md) is available to add some utility
        functions to the social login, for example captcha, email verification, etc.
