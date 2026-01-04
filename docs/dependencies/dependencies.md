# Dependencies

AuthX provides FastAPI dependencies for token validation and retrieval.

## Token Validation Dependencies

These dependencies protect routes and return the validated token payload.

### `access_token_required`

Requires a valid access token:

```python
from fastapi import FastAPI, Depends
from authx import AuthX, AuthXConfig, TokenPayload

app = FastAPI()
auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="your-secret-key"))
auth.handle_errors(app)


@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Access granted"}


# Or get the payload:
@app.get("/me")
def get_me(payload: TokenPayload = Depends(auth.access_token_required)):
    return {"user_id": payload.sub}
```

**Validates:**

- JWT signature and expiration
- Token type is "access"
- CSRF token (if using cookies)

### `refresh_token_required`

Requires a valid refresh token:

```python
@app.post("/refresh")
def refresh(payload: TokenPayload = Depends(auth.refresh_token_required)):
    new_token = auth.create_access_token(uid=payload.sub)
    return {"access_token": new_token}
```

**Validates:**

- JWT signature and expiration
- Token type is "refresh"
- CSRF token (if using cookies)

### `fresh_token_required`

Requires a valid **fresh** access token (for sensitive operations):

```python
@app.post("/change-password", dependencies=[Depends(auth.fresh_token_required)])
def change_password():
    return {"message": "Password changed"}
```

**Validates:**

- Everything `access_token_required` checks
- Token must be fresh (`fresh=True` when created)

## Custom Token Requirements

Use `token_required()` for custom validation:

```python
# Disable CSRF check for a specific route
no_csrf_required = auth.token_required(
    type="access",
    verify_type=True,
    verify_fresh=False,
    verify_csrf=False,  # Disable CSRF
)

@app.post("/api-only")
def api_only(payload: TokenPayload = Depends(no_csrf_required)):
    return {"user_id": payload.sub}
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | `str` | `"access"` | Token type: "access" or "refresh" |
| `verify_type` | `bool` | `True` | Check token type matches |
| `verify_fresh` | `bool` | `False` | Require fresh token |
| `verify_csrf` | `bool` | `None` | Override CSRF check (None = use config) |

## Token Retrieval Dependencies

These dependencies retrieve the token without validating it.

### `get_token_from_request()`

Get a token from the request (may be None):

```python
from authx import RequestToken


@app.get("/check")
async def check_token(request):
    token = await auth.get_token_from_request(request, optional=True)

    if token is None:
        return {"authenticated": False}

    try:
        payload = auth.verify_token(token)
        return {"authenticated": True, "user": payload.sub}
    except Exception:
        return {"authenticated": False, "reason": "invalid token"}
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | `str` | `"access"` | Token type to look for |
| `optional` | `bool` | `True` | If False, raises error when no token found |

### Property Shortcuts

Use these properties as dependencies:

```python
from authx import RequestToken

# Get access token (optional)
@app.get("/info")
def get_info(token: RequestToken = auth.ACCESS_TOKEN):
    if token:
        return {"token_location": token.location}
    return {"message": "No token"}

# Get refresh token (optional)
@app.post("/refresh-info")
def refresh_info(token: RequestToken = auth.REFRESH_TOKEN):
    if token:
        return {"has_refresh": True}
    return {"has_refresh": False}
```

## RequestToken vs TokenPayload

| Type | What It Is | Validated? |
|------|------------|------------|
| `RequestToken` | Raw token from request | No |
| `TokenPayload` | Decoded and validated token | Yes |

**RequestToken fields:**

- `token` - The raw JWT string
- `location` - Where it was found ("headers", "cookies", etc.)
- `csrf` - CSRF token (if from cookies)
- `type` - Expected type ("access" or "refresh")

**TokenPayload fields:**

- `sub` - Subject (user ID)
- `exp` - Expiration timestamp
- `iat` - Issued at timestamp
- `type` - Token type
- `fresh` - Whether token is fresh

## Complete Example

```python
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig, TokenPayload, RequestToken

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


@app.post("/login")
def login(username: str, password: str):
    if username == "test" and password == "test":
        return {"access_token": auth.create_access_token(uid=username, fresh=True)}
    raise HTTPException(401, detail="Invalid credentials")


# Route level dependency - just protects the route
@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Access granted"}


# Get payload in function
@app.get("/me")
def get_me(payload: TokenPayload = Depends(auth.access_token_required)):
    return {"user_id": payload.sub, "token_type": payload.type}


# Fresh token for sensitive operations
@app.post("/delete-account", dependencies=[Depends(auth.fresh_token_required)])
def delete_account():
    return {"message": "Account deleted"}


# Optional token - doesn't require authentication
@app.get("/greeting")
async def greeting(request):
    token = await auth.get_token_from_request(request, optional=True)
    if token:
        try:
            payload = auth.verify_token(token)
            return {"message": f"Hello, {payload.sub}!"}
        except Exception:
            pass
    return {"message": "Hello, guest!"}
```
