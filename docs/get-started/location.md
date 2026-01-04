# JWT Locations

AuthX can read tokens from multiple locations: headers, cookies, query parameters, or JSON body.

## Quick Reference

| Location | Best For | CSRF Protection |
|----------|----------|-----------------|
| Headers | APIs, Mobile apps | Not needed |
| Cookies | Web apps | Required |
| Query | Special cases | Not recommended |
| JSON Body | APIs | Not needed |

## Configuration

```python
from authx import AuthX, AuthXConfig

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],  # Default: only headers
)

# Or accept multiple locations:
config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers", "cookies"],
)

auth = AuthX(config=config)
auth.handle_errors(app)
```

---

## Headers (Recommended for APIs)

The default and most common method. Token is sent in the `Authorization` header.

**Configuration:**

```python
config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
    JWT_HEADER_NAME="Authorization",  # Default
    JWT_HEADER_TYPE="Bearer",         # Default
)
```

**Usage:**

=== "cURL"
    ```bash
    curl -H "Authorization: Bearer <token>" http://localhost:8000/protected
    ```

=== "JavaScript"
    ```javascript
    fetch("http://localhost:8000/protected", {
      headers: { "Authorization": `Bearer ${token}` }
    });
    ```

=== "Python"
    ```python
    import requests

    requests.get(
        "http://localhost:8000/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    ```

---

## Cookies (Recommended for Web Apps)

Best for browser-based applications. Tokens are stored in HttpOnly cookies.

!!! warning "CSRF Protection Required"
    When using cookies, you **must** handle CSRF protection. AuthX enables this by default.

### Complete Cookie Example

```python
from fastapi import FastAPI, Depends, HTTPException, Response
from pydantic import BaseModel
from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_COOKIE_CSRF_PROTECT=True,        # Enabled by default
    JWT_COOKIE_SECURE=False,             # Set True in production (HTTPS)
)

auth = AuthX(config=config)
auth.handle_errors(app)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginRequest, response: Response):
    if data.username == "test" and data.password == "test":
        token = auth.create_access_token(uid=data.username)

        # IMPORTANT: Use set_access_cookies() - this sets BOTH the JWT cookie AND the CSRF cookie
        auth.set_access_cookies(token, response)

        return {"message": "Logged in"}
    raise HTTPException(401, detail="Invalid credentials")


@app.post("/logout")
def logout(response: Response):
    auth.unset_cookies(response)
    return {"message": "Logged out"}


@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Access granted"}
```

!!! danger "Common Mistake"
    **Do NOT** manually set cookies like this:
    ```python
    # WRONG - Missing CSRF cookie!
    response.set_cookie("access_token_cookie", token)
    ```

    **Always use** `auth.set_access_cookies()` which sets both the JWT cookie and CSRF cookie.

### Making Requests with Cookies

For POST/PUT/PATCH/DELETE requests, include the CSRF token in the header:

=== "JavaScript"
    ```javascript
    // Get CSRF token from cookie
    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // Make authenticated request
    fetch("http://localhost:8000/protected", {
      method: "POST",
      credentials: "include",  // Include cookies
      headers: {
        "X-CSRF-TOKEN": getCookie("csrf_access_token")
      }
    });
    ```

=== "cURL"
    ```bash
    curl -X POST \
      --cookie "access_token_cookie=<token>" \
      -H "X-CSRF-TOKEN: <csrf-token>" \
      http://localhost:8000/protected
    ```

### Disabling CSRF (Not Recommended)

If you're building an API that won't be accessed from browsers:

```python
config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_COOKIE_CSRF_PROTECT=False,  # Disable CSRF
)
```

---

## Query Parameters (Use Sparingly)

Token in URL query string. **Not recommended** - URLs are logged and visible in browser history.

```python
config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["query"],
    JWT_QUERY_STRING_NAME="token",  # Default
)
```

**Usage:**

```bash
curl "http://localhost:8000/protected?token=<token>"
```

!!! warning
    Query strings are visible in logs, browser history, and referrer headers. Use only when necessary.

---

## JSON Body

Token in request body. Requires `Content-Type: application/json`.

```python
config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["json"],
    JWT_JSON_KEY="access_token",        # Default
    JWT_REFRESH_JSON_KEY="refresh_token",  # Default
)
```

**Usage:**

=== "cURL"
    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{"access_token": "<token>"}' \
      http://localhost:8000/protected
    ```

=== "JavaScript"
    ```javascript
    fetch("http://localhost:8000/protected", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ access_token: token })
    });
    ```

---

## Multiple Locations

Accept tokens from multiple locations (AuthX checks in order):

```python
config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers", "cookies", "json", "query"],
)
```

AuthX will check each location in order until it finds a token.

---

## Dual Location Pattern (Access in Header, Refresh in Cookie)

A common and secure pattern for web applications is to use different locations for different token types:

- **Access tokens** in headers: Short-lived, stored in client memory, sent explicitly
- **Refresh tokens** in HTTP-only cookies: Long-lived, secure storage, sent automatically

!!! tip "Why This Pattern?"
    - **Access tokens in memory**: Prevents XSS from stealing long-lived tokens
    - **Refresh tokens in HTTP-only cookies**: Cannot be accessed by JavaScript, automatic CSRF protection
    - **Headers for API calls**: Standard REST pattern, works with any client

### Configuration

```python
from authx import AuthX, AuthXConfig

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers", "cookies"],  # Enable both
    # Cookie settings for refresh token security
    JWT_COOKIE_SECURE=True,         # HTTPS only (set False for local dev)
    JWT_COOKIE_HTTP_ONLY=True,      # Prevent JS access
    JWT_COOKIE_CSRF_PROTECT=True,   # CSRF protection for refresh
)
auth = AuthX(config=config)
```

### Login Endpoint

```python
@app.post("/login")
def login(user: LoginRequest, response: Response):
    # Validate credentials...

    # Create both tokens
    access_token = auth.create_access_token(uid=user.username)
    refresh_token = auth.create_refresh_token(uid=user.username)

    # Set ONLY refresh token in cookie
    auth.set_refresh_cookies(refresh_token, response)

    # Return access token in response body
    return {"access_token": access_token, "token_type": "bearer"}
```

### Protected Endpoints (Access Token from Header)

```python
@app.get("/protected")
async def protected(request: Request):
    # Explicitly get token from headers only
    access_token = await auth.get_access_token_from_request(
        request,
        locations=["headers"],  # Only look in headers
    )
    payload = auth.verify_token(access_token, verify_csrf=False)
    return {"user": payload.sub}
```

### Refresh Endpoint (Refresh Token from Cookie)

```python
@app.post("/refresh")
async def refresh(request: Request):
    # Get refresh token from cookies only
    refresh_token = await auth.get_refresh_token_from_request(
        request,
        locations=["cookies"],  # Only look in cookies
    )
    payload = auth.verify_token(refresh_token)

    # Return new access token in body
    new_access_token = auth.create_access_token(uid=payload.sub)
    return {"access_token": new_access_token, "token_type": "bearer"}
```

### Logout Endpoint

```python
@app.post("/logout")
def logout(response: Response):
    # Clear refresh token cookie
    auth.unset_refresh_cookies(response)
    return {"message": "Logged out"}
```

### Client-Side Flow

=== "JavaScript"
    ```javascript
    // Login - store access token in memory
    const response = await fetch("/login", {
      method: "POST",
      credentials: "include",  // Required for cookies
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const { access_token } = await response.json();

    // Store in memory (NOT localStorage)
    let accessToken = access_token;

    // API calls - send access token in header
    await fetch("/protected", {
      headers: { "Authorization": `Bearer ${accessToken}` }
    });

    // Refresh - cookie sent automatically
    function getCsrfToken() {
      return document.cookie.match(/csrf_refresh_token=([^;]+)/)?.[1];
    }

    const refreshResponse = await fetch("/refresh", {
      method: "POST",
      credentials: "include",
      headers: { "X-CSRF-TOKEN": getCsrfToken() }
    });
    accessToken = (await refreshResponse.json()).access_token;
    ```

See the [dual_token_location.py example](https://github.com/yezz123/authx/blob/main/examples/examples/dual_token_location.py) for a complete implementation.

---

## Cookie Configuration Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `JWT_ACCESS_COOKIE_NAME` | `access_token_cookie` | Cookie name for access token |
| `JWT_REFRESH_COOKIE_NAME` | `refresh_token_cookie` | Cookie name for refresh token |
| `JWT_COOKIE_SECURE` | `True` | Only send over HTTPS |
| `JWT_COOKIE_SAMESITE` | `lax` | SameSite policy |
| `JWT_COOKIE_CSRF_PROTECT` | `True` | Enable CSRF protection |
| `JWT_ACCESS_CSRF_COOKIE_NAME` | `csrf_access_token` | CSRF cookie name |
| `JWT_ACCESS_CSRF_HEADER_NAME` | `X-CSRF-TOKEN` | CSRF header name |
