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
