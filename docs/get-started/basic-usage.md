# Basic Usage

This guide shows you how to add JWT authentication to your FastAPI application using AuthX.

## Complete Example

Here's a fully working example you can copy and run:

```python
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig

app = FastAPI()

# Step 1: Configure AuthX
config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",  # Required: use env variable in production
    JWT_TOKEN_LOCATION=["headers"],    # Where to look for tokens
)

# Step 2: Create AuthX instance
auth = AuthX(config=config)

# Step 3: Register error handlers (important!)
auth.handle_errors(app)

# Step 4: Create login endpoint
@app.post("/login")
def login(username: str, password: str):
    if username == "test" and password == "test":
        token = auth.create_access_token(uid=username)
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")

# Step 5: Protect your routes
@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Hello World"}
```

**Run it:**

```bash
uvicorn main:app --reload
```

**Test it:**

```bash
# Get a token
curl -X POST "http://localhost:8000/login?username=test&password=test"

# Use the token
curl -H "Authorization: Bearer <your-token>" http://localhost:8000/protected
```

## Step-by-Step Breakdown

### 1. Configure AuthX

AuthX uses `AuthXConfig` to customize JWT behavior:

```python
from authx import AuthXConfig

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",  # Required for signing tokens
    JWT_ALGORITHM="HS256",             # Default algorithm
    JWT_TOKEN_LOCATION=["headers"],    # Accept tokens in headers
)
```

!!! warning "Keep Secrets Safe"
    Never hardcode secrets in production. Use environment variables:

    ```python
    import os

    config = AuthXConfig(
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
    )
    ```

### 2. Create AuthX Instance

```python
from authx import AuthX

auth = AuthX(config=config)
```

You can also load config after creation:

```python
auth = AuthX()
auth.load_config(config)
```

### 3. Register Error Handlers

This ensures authentication errors return proper HTTP responses instead of 500 errors:

```python
auth.handle_errors(app)
```

Without this, authentication failures will raise unhandled exceptions.

### 4. Create Access Tokens

Use `create_access_token` to generate a signed JWT for a user:

```python
@app.post("/login")
def login(username: str, password: str):
    if username == "test" and password == "test":
        token = auth.create_access_token(uid=username)
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")
```

The `uid` parameter identifies the user. Use a user ID or UUID, not personal information.

!!! tip "Security Tip"
    In production, use POST with a request body for login, not query parameters:

    ```python
    from pydantic import BaseModel

    class LoginRequest(BaseModel):
        username: str
        password: str

    @app.post("/login")
    def login(data: LoginRequest):
        # Validate credentials...
        token = auth.create_access_token(uid=data.username)
        return {"access_token": token}
    ```

### 5. Protect Routes

Use `access_token_required` as a dependency to protect routes:

```python
@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Hello World"}
```

**What happens:**

- No token → `401 Missing JWT in request`
- Invalid token → `401 Invalid Token`
- Valid token → Route executes normally

## Getting the Current User

To access the token payload in your route:

```python
from authx import TokenPayload

@app.get("/me")
def get_me(payload: TokenPayload = Depends(auth.access_token_required)):
    return {"user_id": payload.sub}
```

The `TokenPayload` contains:

- `sub` - Subject (the `uid` you passed to `create_access_token`)
- `exp` - Expiration time
- `iat` - Issued at time
- `type` - Token type ("access" or "refresh")

## Next Steps

- [Token Locations](./location.md) - Accept tokens from cookies, query params, or JSON body
- [Refresh Tokens](./refresh.md) - Keep users logged in with refresh tokens
- [Token Freshness](./token.md) - Require re-authentication for sensitive operations
