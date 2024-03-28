# Token Freshness

Token freshness mechanisms provide additional protection for sensitive operations. Fresh tokens should only be generated when the user provides credential information during a login operation.

Every time a user authenticates itself with credentials, it receives a `fresh` token. However, when an access token is refreshed (implicitly or explicitly), the generated access token SHOULD NOT be marked as `fresh`.

Most protected endpoints should not consider the `fresh` state of the access token. However, in specific application cases, the use of a `fresh` token enables an additional layer of protection by requiring the user to authenticate itself.

These operations include but are not limited to:

- Password update
- User information update
- Privilege/Permission management

## Combined with an explicit refresh mechanism

Let's use the example from the previous section on [Refreshing tokens](./refresh.md#explicit-refresh).

```python
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, TokenPayload

app = FastAPI()
security = AuthX()

class LoginForm(BaseModel):
    username: str
    password: str

@app.post('/login')
def login(data: LoginForm):
    if data.username == "test" and data.password == "test":
        access_token = security.create_access_token(
            data.username,
            fresh=True
        )
        refresh_token = security.create_refresh_token(data.username)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    raise HTTPException(401, "Bad username/password")

@app.post('/refresh')
def refresh(
    refresh_payload: TokenPayload = Depends(security.refresh_token_required)
):
    access_token = security.create_access_token(
        refresh_payload.sub,
        fresh=False
    )
    return {"access_token": access_token}

@app.get('/protected', dependencies=[Depends(security.access_token_required)])
def protected():
    return "You have access to this protected resource"

@app.get('/sensitive_operation', dependencies=[Depends(security.fresh_token_required)])
def sensitive_operation():
    return "You have access to this sensitive operation"
```

### Creating fresh access tokens

To create a `fresh` access token, use the `fresh=True` argument in the `AuthX.create_access_token` method.

In the `/login` route, we set the `fresh` argument to `True` because the token is generated after the user explicitly provides a username/password combo.

```python
@app.post('/login')
def login(data: LoginForm):
    if data.username == "test" and data.password == "test":
        access_token = security.create_access_token(
            data.username,
            fresh=True
        )
        refresh_token = security.create_refresh_token(data.username)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    raise HTTPException(401, "Bad username/password")
```

!!! note
     By default, `AuthX.create_access_token` has `fresh=False` to avoid implicit fresh token generation.

### Refreshing tokens

When refreshing tokens, you should always generate **non**-`fresh` tokens. In the example below, the `fresh` argument is explicitly set to `False`, which is also the default behavior for `AuthX.create_access_token`.

```python
@app.post('/refresh')
def refresh(
    refresh_payload: TokenPayload = Depends(security.refresh_token_required)
):
    access_token = security.create_access_token(
        refresh_payload.sub,
        fresh=False
    )
    return {"access_token": access_token}
```

### Requiring fresh tokens

The `/protected` route behaves as usual, regardless of the `fresh` token's state.

In contrast, the `/sensitive_operation` route requires a fresh token to be executed. This behavior is defined by the `AuthX.fresh_token_required` dependency.

```python
@app.get('/protected', dependencies=[Depends(security.access_token_required)])
def protected():
    return "You have access to this protected resource"

@app.get('/sensitive_operation', dependencies=[Depends(security.fresh_token_required)])
def sensitive_operation():
    return "You have access to this sensitive operation"
```

=== "1. Login"

    ```shell
    # Logging in to obtain a fresh token
    $ curl -s -X POST --json '{"username":"test", "password":"test"}' http://0.0.0.0:8000/login
    {"access_token": $FRESH_TOKEN, "refresh_token": $REFRESH_TOKEN}
    ```

=== "2. Sensitive Operation"

    ```shell
    # Requesting the sensitive operation with the fresh token
    $ curl -s --oauth2-bearer $FRESH_TOKEN http://0.0.0.0:8000/sensitive_operation
    "You have access to this sensitive operation"
    ```

=== "3. Refresh access token"

    ```shell
    # Refreshing the access token to get a new non-fresh one
    $ curl -s --oauth2-bearer $REFRESH_TOKEN http://0.0.0.0:8000/refresh
    {"access_token": $NON_FRESH_TOKEN}
    ```

=== "4. Sensitive operation"

    ```shell
    # Requesting the sensitive operation with the non-fresh token
    $ curl -s --oauth2-bearer $FRESH_TOKEN http://0.0.0.0:8000/sensitive_operation
    Internal server error
    ```

??? note "Note on Internal server error"
     As you might notice, step 4 results in a 500 HTTP Internal Server Error. This is the expected behavior since error handling is by default disabled on AuthX and should be enabled or handled by you to avoid errors.
