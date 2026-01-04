# Dependency Bundle

The `AuthXDependency` bundle provides access to AuthX methods within route context, simplifying cookie operations.

## Why Use It?

When setting cookies, you need access to the response object. The bundle provides this automatically:

=== "With Bundle (Simpler)"
    ```python
    from fastapi import FastAPI
    from authx import AuthX, AuthXConfig, AuthXDependency

    app = FastAPI()

    config = AuthXConfig(
        JWT_SECRET_KEY="your-secret-key",
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_COOKIE_SECURE=False,
    )

    auth = AuthX(config=config)
    auth.handle_errors(app)

    @app.post("/login")
    def login(deps: AuthXDependency = auth.BUNDLE):
        token = deps.create_access_token(uid="user")
        deps.set_access_cookies(token)  # No response object needed!
        return {"message": "Logged in"}

    @app.post("/logout", dependencies=[auth.ACCESS_REQUIRED])
    def logout(deps: AuthXDependency = auth.BUNDLE):
        deps.unset_cookies()
        return {"message": "Logged out"}
    ```

=== "Without Bundle"
    ```python
    from fastapi import FastAPI, Response
    from authx import AuthX, AuthXConfig

    app = FastAPI()

    config = AuthXConfig(
        JWT_SECRET_KEY="your-secret-key",
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_COOKIE_SECURE=False,
    )

    auth = AuthX(config=config)
    auth.handle_errors(app)

    @app.post("/login")
    def login(response: Response):
        token = auth.create_access_token(uid="user")
        auth.set_access_cookies(token, response)  # Must pass response
        return {"message": "Logged in"}

    @app.post("/logout", dependencies=[auth.ACCESS_REQUIRED])
    def logout(response: Response):
        auth.unset_cookies(response)  # Must pass response
        return {"message": "Logged out"}
    ```

## Available Methods

The bundle provides all AuthX methods with automatic request/response context:

| Method | Description |
|--------|-------------|
| `create_access_token(uid, ...)` | Create access token |
| `create_refresh_token(uid, ...)` | Create refresh token |
| `set_access_cookies(token)` | Set access token cookie |
| `set_refresh_cookies(token)` | Set refresh token cookie |
| `unset_cookies()` | Remove all auth cookies |
| `unset_access_cookies()` | Remove access token cookie |
| `unset_refresh_cookies()` | Remove refresh token cookie |

## Complete Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from authx import AuthX, AuthXConfig, AuthXDependency

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_COOKIE_SECURE=False,  # Set True in production (HTTPS)
)

auth = AuthX(config=config)
auth.handle_errors(app)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginRequest, deps: AuthXDependency = auth.BUNDLE):
    if data.username == "test" and data.password == "test":
        access_token = deps.create_access_token(uid=data.username)
        refresh_token = deps.create_refresh_token(uid=data.username)
        deps.set_access_cookies(access_token)
        deps.set_refresh_cookies(refresh_token)
        return {"message": "Logged in"}
    raise HTTPException(401, detail="Invalid credentials")


@app.post("/refresh")
def refresh(payload=auth.REFRESH_REQUIRED, deps: AuthXDependency = auth.BUNDLE):
    access_token = deps.create_access_token(uid=payload.sub)
    deps.set_access_cookies(access_token)
    return {"message": "Token refreshed"}


@app.post("/logout", dependencies=[auth.ACCESS_REQUIRED])
def logout(deps: AuthXDependency = auth.BUNDLE):
    deps.unset_cookies()
    return {"message": "Logged out"}


@app.get("/protected", dependencies=[auth.ACCESS_REQUIRED])
def protected():
    return {"message": "Access granted"}
```

## Testing

```bash
# Login (sets cookies)
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test", "password":"test"}' \
  -c cookies.txt \
  http://localhost:8000/login

# Access protected route (uses cookies)
curl -b cookies.txt http://localhost:8000/protected

# Logout (clears cookies)
curl -X POST -b cookies.txt -c cookies.txt http://localhost:8000/logout
```
