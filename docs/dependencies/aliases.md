# Dependency Aliases

If you are familiar with [FastAPI Dependency Injection system](https://fastapi.tiangolo.com/tutorial/dependencies/),
you know you need to import the `Depends` object to declare a dependency.
Since AuthX is designed to work with FastAPI, we provide quick aliases to get the most accessed dependencies.

The following example demonstrate how AuthX aliases can help you reduce verbosity.

=== "Without aliases"

    ```py
    from fastapi import FastAPI, Depends
    from authx import AuthX

    app = FastAPI()
    security = AuthX()
    security.handle_errors(app)

    @app.route('/', dependencies=[Depends(security.access_token_required)])
    def root(subject = Depends(security.get_current_subject), token = Depends(security.get_token_from_request)):
        ...
    ```

=== "With aliases"

    ```py
    from fastapi import FastAPI
    from authx import AuthX

    app = FastAPI()
    security = AuthX()
    security.handle_errors(app)

    @app.route('/', dependencies=[security.ACCESS_REQUIRED])
    def root(subject = security.CURRENT_SUBJECT, token = security.RAW_ACCESS_TOKEN):
        ...
    ```

## Aliases

### `ACCESS_REQUIRED`

- [`TokenPayload`](../api/token.md)

Returns the access token payload if valid. Enforce the access token validation

#### example

```py
from fastapi import FastAPI
from authx import AuthX

app = FastAPI()
security = AuthX()

@app.route('/protected')
def protected(payload = security.ACCESS_REQUIRED):
    return f"Your Access Token Payload is {payload}"
```

### `ACCESS_TOKEN`

- [`RequestToken`](../api/request.md)

Returns the encoded access token. **DOES NOT** Enforce the access token validation

#### example

```py
from fastapi import FastAPI
from authx import AuthX

app = FastAPI()
security = AuthX()

# Use route dependency to enforce validation in conjunction with ACCESS_TOKEN
@app.route('/protected', dependencies=[security.ACCESS_REQUIRED])
def protected(token = security.ACCESS_TOKEN):
    return f"Your Access Token is {token}"
```

### `REFRESH_REQUIRED`

- [`TokenPayload`](../api/token.md)

Returns the refresh token payload if valid. Enforce the refresh token validation

#### example

```py
from fastapi import FastAPI
from authx import AuthX

app = FastAPI()
security = AuthX()

@app.route('/refresh')
def refresh(payload = security.REFRESH_REQUIRED):
    return f"Your Refresh Token Payload is {payload}"
```

### `REFRESH_TOKEN`

- [`RequestToken`](../api/request.md)

Returns the encoded refresh token. **DOES NOT** Enforce the refresh token validation

#### example

```py
from fastapi import FastAPI
from authx import AuthX

app = FastAPI()
security = AuthX()

# Use route dependency to enforce validation in conjunction with REFRESH_TOKEN
@app.route('/refresh', dependencies=[security.REFRESH_REQUIRED])
def refresh(token = security.REFRESH_TOKEN):
    return f"Your Refresh Token is {token}"
```

### `FRESH_REQUIRED`

- [`TokenPayload`](../api/token.md)

Returns the access token payload if valid & **FRESH**. Enforce the access token validation

#### example

```py
from fastapi import FastAPI
from authx import AuthX

app = FastAPI()
security = AuthX()

@app.route('/protected', dependencies=[security.FRESH_REQUIRED])
def protected():
    return "Congratulations! Your have a fresh and valid access token."
```

### `CURRENT_SUBJECT`

- `Any`

Returns the current subject. Enforce the access token validation

!!! note
    You must set a subject getter to use this dependency. See [Callbacks > User Serialization](../callbacks/user.md)

#### example

```py
from fastapi import FastAPI
from authx import AuthX

app = FastAPI()
security = AuthX()

@app.route('/whoami')
def whoami(subject = security.CURRENT_SUBJECT):
    return f"You are: {subject}"
```

### `BUNDLE` / `DEPENDENCY`

- [`AuthXDependency`](../api/dependencies.md)

Returns the [`AuthXDependency`](./bundle.md) dependency bundle to be used within the route

#### example

```py
from fastapi import FastAPI
from authx import AuthX

app = FastAPI()
security = AuthX()

@app.route('/create_token')
def create_token(auth = security.BUNDLE):
    token = auth.create_access_token(uid="test")
    auth.set_access_cookie(token)
    return "OK"
```
