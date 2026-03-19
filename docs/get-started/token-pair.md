# Token Pairs

Most authentication flows require creating both an access token and a refresh token at once. AuthX provides `create_token_pair()` and `TokenResponse` to eliminate this boilerplate.

## The Problem

Without `create_token_pair`, every login endpoint repeats the same pattern:

```python
@app.post("/login")
def login(data: LoginRequest):
    access_token = auth.create_access_token(uid=data.username)
    refresh_token = auth.create_refresh_token(uid=data.username)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
```

## Complete Example

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from authx import AuthX, AuthXConfig, TokenPayload, TokenResponse

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    """Returns access + refresh tokens in one call."""
    if data.username == "test" and data.password == "test":
        return auth.create_token_pair(uid=data.username)
    raise HTTPException(401, detail="Invalid credentials")


@app.post("/refresh", response_model=TokenResponse)
def refresh(payload: TokenPayload = Depends(auth.refresh_token_required)):
    """Exchange refresh token for a new token pair."""
    return auth.create_token_pair(uid=payload.sub)


@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "You have access"}
```

The response is a standardized JSON object:

```json
{
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
}
```

## Testing the Flow

```bash
# 1. Login to get a token pair
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test", "password":"test"}' \
  http://localhost:8000/login
# {"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer"}

# 2. Access protected route
curl -H "Authorization: Bearer <access-token>" \
  http://localhost:8000/protected
# {"message": "You have access"}

# 3. Refresh to get a new pair
curl -X POST -H "Authorization: Bearer <refresh-token>" \
  http://localhost:8000/refresh
# {"access_token": "eyJ...", "refresh_token": "eyJ...", "token_type": "bearer"}
```

---

## Parameters

`create_token_pair()` accepts all the options from `create_access_token` and `create_refresh_token`, with separate control for each token:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `uid` | `str` | **required** | User identifier stored in the `sub` claim |
| `fresh` | `bool` | `False` | Mark the access token as fresh |
| `headers` | `dict` | `None` | Custom JWT headers for both tokens |
| `access_expiry` | `timedelta` | config default | Override access token expiration |
| `refresh_expiry` | `timedelta` | config default | Override refresh token expiration |
| `data` | `dict` | `None` | Additional claims added to both tokens |
| `audience` | `str` | `None` | Audience claim for both tokens |
| `access_scopes` | `list[str]` | `None` | Scopes for the access token only |
| `refresh_scopes` | `list[str]` | `None` | Scopes for the refresh token only |

---

## With Scopes

You can assign different scopes to access and refresh tokens:

```python
@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = get_user(data.username)
    return auth.create_token_pair(
        uid=user.id,
        access_scopes=user.permissions,    # e.g. ["users:read", "posts:write"]
        refresh_scopes=["token:refresh"],   # Limited scope for refresh token
    )
```

---

## With Custom Expiry

Set independent expiration for access and refresh tokens:

```python
from datetime import timedelta

tokens = auth.create_token_pair(
    uid="user123",
    access_expiry=timedelta(minutes=30),
    refresh_expiry=timedelta(days=7),
)
```

---

## With Fresh Tokens

Mark the access token as fresh for sensitive operations:

```python
@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    """Login creates a fresh token pair."""
    return auth.create_token_pair(uid=data.username, fresh=True)


@app.post("/refresh", response_model=TokenResponse)
def refresh(payload: TokenPayload = Depends(auth.refresh_token_required)):
    """Refresh creates a non-fresh token pair."""
    return auth.create_token_pair(uid=payload.sub, fresh=False)
```

See [Token Freshness](./token.md) for more on fresh vs non-fresh tokens.

---

## With the Dependency Bundle

`create_token_pair` is also available on the `AuthXDependency` bundle:

```python
from authx import AuthXDependency

@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, deps: AuthXDependency = auth.BUNDLE):
    """Use the bundle for cookie-based flows."""
    tokens = deps.create_token_pair(uid=data.username)
    deps.set_access_cookies(tokens.access_token)
    deps.set_refresh_cookies(tokens.refresh_token)
    return tokens
```

See [Dependency Bundle](../dependencies/bundle.md) for more details.

---

## TokenResponse Schema

`TokenResponse` is a Pydantic model you can use as a FastAPI `response_model`:

```python
from authx import TokenResponse

# Fields:
# - access_token: str
# - refresh_token: str
# - token_type: str = "bearer"

# Use as response_model for OpenAPI documentation
@app.post("/login", response_model=TokenResponse)
def login():
    ...
```

This generates proper OpenAPI/Swagger documentation for your login endpoints automatically.

---

## Next Steps

- [Refresh Tokens](./refresh.md) - Understanding refresh token flows
- [Token Freshness](./token.md) - Require re-authentication for sensitive operations
- [Scope Management](./scopes.md) - Fine-grained access control with scopes
- [Dependency Bundle](../dependencies/bundle.md) - Simplified cookie management
