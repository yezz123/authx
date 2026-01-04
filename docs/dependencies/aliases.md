# Dependency Aliases

AuthX provides shorthand properties to reduce verbosity when using dependencies.

## Before and After

=== "Without Aliases"
    ```python
    from fastapi import FastAPI, Depends
    from authx import AuthX, AuthXConfig

    app = FastAPI()
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    auth.handle_errors(app)

    @app.get("/", dependencies=[Depends(auth.access_token_required)])
    def root(payload=Depends(auth.access_token_required)):
        return {"user": payload.sub}
    ```

=== "With Aliases"
    ```python
    from fastapi import FastAPI
    from authx import AuthX, AuthXConfig

    app = FastAPI()
    auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="secret"))
    auth.handle_errors(app)

    @app.get("/", dependencies=[auth.ACCESS_REQUIRED])
    def root(payload=auth.ACCESS_REQUIRED):
        return {"user": payload.sub}
    ```

## Available Aliases

### ACCESS_REQUIRED

Requires a valid access token. Returns `TokenPayload`.

```python
@app.get("/protected")
def protected(payload=auth.ACCESS_REQUIRED):
    return {"user": payload.sub}
```

### REFRESH_REQUIRED

Requires a valid refresh token. Returns `TokenPayload`.

```python
@app.post("/refresh")
def refresh(payload=auth.REFRESH_REQUIRED):
    new_token = auth.create_access_token(uid=payload.sub)
    return {"access_token": new_token}
```

### FRESH_REQUIRED

Requires a valid **fresh** access token. Returns `TokenPayload`.

```python
@app.post("/change-password", dependencies=[auth.FRESH_REQUIRED])
def change_password():
    return {"message": "Password changed"}
```

### ACCESS_TOKEN

Gets the raw access token (not validated). Returns `RequestToken` or `None`.

```python
@app.get("/token-info", dependencies=[auth.ACCESS_REQUIRED])
def token_info(token=auth.ACCESS_TOKEN):
    return {"location": token.location}
```

### REFRESH_TOKEN

Gets the raw refresh token (not validated). Returns `RequestToken` or `None`.

```python
@app.post("/refresh-info", dependencies=[auth.REFRESH_REQUIRED])
def refresh_info(token=auth.REFRESH_TOKEN):
    return {"token": token.token[:20] + "..."}
```

### CURRENT_SUBJECT

Gets the current user via subject getter. Requires `@auth.set_subject_getter`.

```python
@auth.set_subject_getter
def get_user(uid: str):
    return {"id": uid, "name": "User"}

@app.get("/me")
def get_me(user=auth.CURRENT_SUBJECT):
    return user
```

### BUNDLE / DEPENDENCY

Gets `AuthXDependency` for cookie operations within routes.

```python
@app.post("/login")
def login(deps=auth.BUNDLE):
    token = deps.create_access_token(uid="user")
    deps.set_access_cookies(token)
    return {"message": "Logged in"}
```

## Complete Example

```python
from fastapi import FastAPI
from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


@app.get("/login")
def login():
    return {"access_token": auth.create_access_token(uid="user123", fresh=True)}


@app.get("/protected", dependencies=[auth.ACCESS_REQUIRED])
def protected():
    return {"message": "Access granted"}


@app.get("/me")
def get_me(payload=auth.ACCESS_REQUIRED):
    return {"user_id": payload.sub}


@app.post("/sensitive", dependencies=[auth.FRESH_REQUIRED])
def sensitive():
    return {"message": "Sensitive operation complete"}
```
