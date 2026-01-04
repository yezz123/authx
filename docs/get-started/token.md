# Token Freshness

Fresh tokens provide extra security for sensitive operations. A token is "fresh" only when the user has just authenticated with their credentials.

## When to Use Fresh Tokens

Require fresh tokens for sensitive operations:

- Password changes
- Email updates
- Payment actions
- Account deletion

Regular protected routes don't need fresh tokens.

## Complete Example

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from authx import AuthX, AuthXConfig, TokenPayload

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


@app.post("/login")
def login(data: LoginRequest):
    """Login returns a FRESH access token and a refresh token."""
    if data.username == "test" and data.password == "test":
        # fresh=True because user just entered credentials
        access_token = auth.create_access_token(uid=data.username, fresh=True)
        refresh_token = auth.create_refresh_token(uid=data.username)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    raise HTTPException(401, detail="Invalid credentials")


@app.post("/refresh")
def refresh(payload: TokenPayload = Depends(auth.refresh_token_required)):
    """Refresh returns a NON-FRESH access token."""
    # fresh=False because user didn't re-enter credentials
    access_token = auth.create_access_token(uid=payload.sub, fresh=False)
    return {"access_token": access_token}


@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    """Any valid token works here."""
    return {"message": "You have access"}


@app.post("/change-password", dependencies=[Depends(auth.fresh_token_required)])
def change_password():
    """Only FRESH tokens work here."""
    return {"message": "Password changed"}
```

## How It Works

### 1. Login Creates Fresh Token

When the user logs in with username/password, create a fresh token:

```python
access_token = auth.create_access_token(uid=data.username, fresh=True)
```

### 2. Refresh Creates Non-Fresh Token

When refreshing, the user didn't re-authenticate, so the token is not fresh:

```python
access_token = auth.create_access_token(uid=payload.sub, fresh=False)
```

!!! note
    `fresh=False` is the default, so you can omit it.

### 3. Protect Sensitive Routes

Use `fresh_token_required` for operations that need recent authentication:

```python
@app.post("/change-password", dependencies=[Depends(auth.fresh_token_required)])
def change_password():
    return {"message": "Password changed"}
```

If a non-fresh token is used, the user gets a `401 Fresh token required` error.

## Testing the Flow

```bash
# 1. Login to get a fresh token
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test", "password":"test"}' \
  http://localhost:8000/login
# Returns: {"access_token": "...", "refresh_token": "..."}

# 2. Access sensitive route with fresh token - WORKS
curl -H "Authorization: Bearer <fresh-token>" \
  -X POST http://localhost:8000/change-password
# Returns: {"message": "Password changed"}

# 3. Refresh the token
curl -H "Authorization: Bearer <refresh-token>" \
  -X POST http://localhost:8000/refresh
# Returns: {"access_token": "..."}  (non-fresh)

# 4. Access sensitive route with non-fresh token - FAILS
curl -H "Authorization: Bearer <non-fresh-token>" \
  -X POST http://localhost:8000/change-password
# Returns: {"message": "Fresh token required", "error_type": "FreshTokenRequiredError"}

# 5. Access regular protected route with non-fresh token - WORKS
curl -H "Authorization: Bearer <non-fresh-token>" \
  http://localhost:8000/protected
# Returns: {"message": "You have access"}
```

## Summary

| Token Type | Created When | Can Access `/protected` | Can Access `/change-password` |
|------------|--------------|-------------------------|-------------------------------|
| Fresh | User logs in with credentials | Yes | Yes |
| Non-Fresh | Token is refreshed | Yes | No |
