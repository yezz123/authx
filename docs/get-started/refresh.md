# Refresh Tokens

Access tokens expire quickly for security. Refresh tokens let users stay logged in without re-entering credentials.

## How It Works

1. User logs in → Gets **access token** (short-lived) + **refresh token** (long-lived)
2. Access token expires → User calls `/refresh` with refresh token
3. Server returns new access token → User continues without re-login

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
    """Returns both access and refresh tokens."""
    if data.username == "test" and data.password == "test":
        access_token = auth.create_access_token(uid=data.username)
        refresh_token = auth.create_refresh_token(uid=data.username)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    raise HTTPException(401, detail="Invalid credentials")


@app.post("/refresh")
def refresh(payload: TokenPayload = Depends(auth.refresh_token_required)):
    """Exchange refresh token for new access token."""
    access_token = auth.create_access_token(uid=payload.sub)
    return {"access_token": access_token}


@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    """Requires valid access token."""
    return {"message": "You have access"}
```

## Testing the Flow

```bash
# 1. Login to get both tokens
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test", "password":"test"}' \
  http://localhost:8000/login
# {"access_token": "eyJ...", "refresh_token": "eyJ..."}

# 2. Access protected route with access token
curl -H "Authorization: Bearer <access-token>" \
  http://localhost:8000/protected
# {"message": "You have access"}

# 3. When access token expires, use refresh token to get a new one
curl -X POST -H "Authorization: Bearer <refresh-token>" \
  http://localhost:8000/refresh
# {"access_token": "eyJ..."}  (new access token)

# 4. Use new access token
curl -H "Authorization: Bearer <new-access-token>" \
  http://localhost:8000/protected
# {"message": "You have access"}
```

## Token Expiration

Configure expiration times in `AuthXConfig`:

```python
from datetime import timedelta

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),   # Short-lived
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),     # Long-lived
)
```

## Important Notes

!!! warning "Protect Your Refresh Tokens"
    Refresh tokens are powerful - they can generate new access tokens. Store them securely:

    - Use HttpOnly cookies when possible
    - Never expose in URLs or logs
    - Implement token revocation for logout

!!! tip "Token Revocation"
    When a user logs out, revoke both tokens. See [Token Callbacks](../callbacks/token.md) for implementing a blocklist.

## Cookie-Based Refresh (Web Apps)

For web applications, store tokens in cookies:

```python
from fastapi import Response

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_COOKIE_CSRF_PROTECT=True,  # Important for security!
)

auth = AuthX(config=config)
auth.handle_errors(app)


@app.post("/login")
def login(data: LoginRequest, response: Response):
    if data.username == "test" and data.password == "test":
        access_token = auth.create_access_token(uid=data.username)
        refresh_token = auth.create_refresh_token(uid=data.username)

        # Set cookies (includes CSRF tokens automatically)
        auth.set_access_cookies(access_token, response)
        auth.set_refresh_cookies(refresh_token, response)

        return {"message": "Logged in"}
    raise HTTPException(401, detail="Invalid credentials")


@app.post("/logout")
def logout(response: Response):
    auth.unset_cookies(response)
    return {"message": "Logged out"}
```

See [JWT Locations](./location.md) for more details on cookie authentication.
