# Dependencies

## Request token dependencies

Sometimes, you may need to access data relative to JWT authentication in a request. Such data might include the encoded JWT, the CSRF double submit token, or the location of the JWT.

To retrieve this information from a request, AuthX provides `AuthX.get_token_from_request`.

`get_token_from_request` allows you to specify the token type you wish to retrieve with the `type` argument and to enforce token availability with the `optional` argument.

```py
from fastapi import FastAPI, Depends
from authx import AuthX, RequestToken

app = FastAPI()
security = AuthX()

TokenGetter = Callable[[Request], Awaitable[RequestToken]]
OptTokenGetter = Callable[[Request], Awaitable[RequestToken | None]]


get_access_from_request: TokenGetter = security.get_token_from_request(
    type: TokenType = "access",
    optional: bool = False
)

get_optional_refresh_from_request: OptTokenGetter = security.get_token_from_request(
    type: TokenType = "access",
    optional: bool = False
)

@app.get('/get_token')
async def get_token(token: RequestToken = Depends(get_access_from_request)):
    ...
```

Please note that even if `optional` is set to `False`, the route will raise an error only because no token is available in the request and not because the token in the request has been invalidated.

`get_token_from_request` dependencies do not provide token validation. This dependency only looks for the token's presence in the request.

## Token validation dependencies

AuthX provides three main dependencies for token requirements.

These methods are AuthX properties returning a FastAPI dependency `Callable[[Request], TokenPayload]`. When these dependencies are resolved, they return a `TokenPayload`.

### `AuthX.access_token_required`

`access_token_required` is a property returning a FastAPI dependency to enforce the presence and validity of an `access` token in the request. This dependency will apply the following verification:

- [X] JWT Validation: verify `exp`, `iat`, `nbf`, `iss`, `aud` claims
- [X] Token type verification: `access` only
- [X] CSRF double submit verification: if CSRF enabled and token location in cookies
- [ ] Token freshness: not required for this dependency

### `AuthX.refresh_token_required`

`refresh_token_required` is a property returning a FastAPI dependency to enforce the presence and validity of a `refresh` token in the request. This dependency will apply the following verification:

- [X] JWT Validation: verify `exp`, `iat`, `nbf`, `iss`, `aud` claims
- [X] Token type verification: `request` only
- [X] CSRF double submit verification: if CSRF enabled and token location in cookies
- [ ] Token freshness: not required for this dependency

### `AuthX.fresh_token_required`

`access_token_required` is a property returning a FastAPI dependency to enforce the presence and validity of an `access` token in the request. It also needs the token to be `fresh`. This dependency will apply the following verification:

- [X] JWT Validation: verify `exp`, `iat`, `nbf`, `iss`, `aud` claims
- [X] Token type verification: `access` only
- [X] CSRF double submit verification: if CSRF enabled and token location in cookies
- [X] Token freshness: not required for this dependency

## Additional token dependency

In addition to the three dependencies specified above, AuthX provides `AuthX.token_required` as an additional layer of customization for token requirements.

```py
from fastapi import FastAPI, Depends
from authx import AuthX, TokenPayload

app = FastAPI()
security = AuthX()

access_token_required = security.token_required(
    type: str = "access",
    verify_type: bool = True,
    verify_fresh: bool = False,
    verify_csrf: Optional[bool] = None
)
fresh_token_required = security.token_required(
    type: str = "access",
    verify_type: bool = True,
    verify_fresh: bool = True,
    verify_csrf: Optional[bool] = None
)
refresh_token_required = security.token_required(
    type: str = "refresh",
    verify_type: bool = True,
    verify_fresh: bool = False,
    verify_csrf: Optional[bool] = None
)

no_csrf_required = security.token_required(
    type: str = "access",
    verify_type: bool = True,
    verify_fresh: bool = False,
    verify_csrf: Optional[bool] = False
)

@app.post('/no_csrf')
def post_no_csrf(payload: TokenPayload = Depends(no_csrf_required)):
    # This function is protected but does not require
    # CSRF double submit token in case of authentication via Cookies
    # This is useful for API calls that are not protected by CSRF
    # but are protected by other means
    ...
```

We have regenerated the main token dependencies from the `AuthX.token_required` method in the highlighted section. `AuthX.token_required` returns a Callable to be used as a dependency.

`(str, bool, bool, Optional[bool]) -> Callable[[Request], TokenPayload]`

As a custom token validation dependency, we have created `no_csrf_required`. This dependency requires a valid `access` token in the request, but it will not execute CSRF validation if the token is located in cookies.

!!! note "Work in progress"
    The `verify_csrf` argument is an optional boolean to enable/disable CSRF protection. If `None`, it uses the default `AuthXConfig.JWT_COOKIE_CSRF_PROTECT` settings to determine if CSRF protection is enabled or not.
