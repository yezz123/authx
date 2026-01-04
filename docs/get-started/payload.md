# Token Payload

The `TokenPayload` contains all the data stored in a JWT. You can access it in your routes and store custom data in tokens.

## Accessing Payload Data

Use `access_token_required` as a dependency to get the payload:

```python
from fastapi import FastAPI, Depends
from authx import AuthX, AuthXConfig, TokenPayload

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


@app.get("/login")
def login():
    token = auth.create_access_token(uid="user123")
    return {"access_token": token}


@app.get("/me")
def get_me(payload: TokenPayload = Depends(auth.access_token_required)):
    return {
        "user_id": payload.sub,
        "token_type": payload.type,
        "is_fresh": payload.fresh,
    }
```

## TokenPayload Fields

| Field | Type | Description |
|-------|------|-------------|
| `sub` | `str` | Subject - the user ID you passed to `create_access_token(uid=...)` |
| `type` | `str` | Token type: "access" or "refresh" |
| `exp` | `datetime` | Expiration time |
| `iat` | `datetime` | Issued at time |
| `fresh` | `bool` | Whether token is fresh |
| `jti` | `str` | Unique token identifier |

## Storing Custom Data

Pass additional data when creating tokens:

```python
@app.get("/login")
def login():
    token = auth.create_access_token(
        uid="user123",
        data={
            "role": "admin",
            "permissions": ["read", "write"],
        }
    )
    return {"access_token": token}


@app.get("/me")
def get_me(payload: TokenPayload = Depends(auth.access_token_required)):
    return {
        "user_id": payload.sub,
        "role": payload.extra_dict.get("role"),
        "permissions": payload.extra_dict.get("permissions"),
    }
```

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


# Mock user database
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}


@app.post("/login")
def login(data: LoginRequest):
    user = USERS.get(data.username)
    if user and user["password"] == data.password:
        token = auth.create_access_token(
            uid=data.username,
            data={"role": user["role"]}
        )
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")


@app.get("/me")
def get_me(payload: TokenPayload = Depends(auth.access_token_required)):
    return {
        "username": payload.sub,
        "role": payload.extra_dict.get("role"),
        "expires_in": str(payload.time_until_expiry),
    }


@app.get("/admin-only")
def admin_only(payload: TokenPayload = Depends(auth.access_token_required)):
    if payload.extra_dict.get("role") != "admin":
        raise HTTPException(403, detail="Admin access required")
    return {"message": "Welcome, admin!"}
```

## Testing

```bash
# Login as admin
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"admin123"}' \
  http://localhost:8000/login

# Get user info
curl -H "Authorization: Bearer <token>" http://localhost:8000/me
# {"username": "admin", "role": "admin", "expires_in": "0:14:59.123456"}

# Access admin route
curl -H "Authorization: Bearer <token>" http://localhost:8000/admin-only
# {"message": "Welcome, admin!"}
```

## Useful Payload Properties

```python
@app.get("/token-info")
def token_info(payload: TokenPayload = Depends(auth.access_token_required)):
    return {
        "user_id": payload.sub,
        "issued_at": payload.issued_at.isoformat(),
        "expires_at": payload.expiry_datetime.isoformat(),
        "time_until_expiry": str(payload.time_until_expiry),
        "time_since_issued": str(payload.time_since_issued),
        "is_fresh": payload.fresh,
        "custom_data": payload.extra_dict,
    }
```
