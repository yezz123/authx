# Using with Template Engines (Jinja2)

AuthX works seamlessly with server-side rendered (SSR) applications using template engines like Jinja2. This guide covers the key differences from API authentication and provides a complete example.

## Key Differences from API Authentication

| Aspect | API (JSON) | Templates (SSR) |
|--------|------------|-----------------|
| Token Location | Headers | Cookies |
| Response Type | JSON | HTML/Redirect |
| Error Handling | HTTP status codes | Redirect to login |
| CSRF | Optional | **Required** for forms |

## Quick Setup

### 1. Configuration

For template-based apps, use cookie authentication:

```python
from authx import AuthX, AuthXConfig

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    # Cookie-based auth for SSR
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_COOKIE_SECURE=False,      # True in production (HTTPS)
    JWT_COOKIE_HTTP_ONLY=True,    # Prevent JS access to token
    # CSRF protection for forms
    JWT_COOKIE_CSRF_PROTECT=True,
    JWT_CSRF_CHECK_FORM=True,     # Check CSRF in form data
    JWT_ACCESS_CSRF_FIELD_NAME="csrf_token",
)

auth = AuthX(config=config)
```

### 2. Setup Jinja2 Templates

```python
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
```

---

## Authentication Flow

### Login Page (GET)

Render the login form:

```python
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error}
    )
```

### Login Submit (POST)

Handle form submission, set cookies, redirect:

```python
from fastapi import Form
from fastapi.responses import RedirectResponse

@app.post("/login")
async def login_submit(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
):
    # Validate credentials
    if not validate_user(username, password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=401
        )

    # Create token and set cookie
    access_token = auth.create_access_token(uid=username)

    redirect = RedirectResponse(url="/dashboard", status_code=303)
    auth.set_access_cookies(access_token, redirect)

    return redirect
```

### Logout

Clear cookies and redirect:

```python
@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    auth.unset_cookies(response)
    return response
```

---

## Protected Routes

### Redirect-Based Auth Dependency

Create a dependency that redirects to login instead of returning 401:

```python
from authx.exceptions import AuthXException

class RedirectToLogin(Exception):
    def __init__(self, url: str = "/login"):
        self.url = url

@app.exception_handler(RedirectToLogin)
async def redirect_handler(request: Request, exc: RedirectToLogin):
    return RedirectResponse(url=exc.url, status_code=303)

async def require_auth(request: Request) -> dict:
    """Dependency that redirects to login if not authenticated."""
    try:
        token = await auth.get_access_token_from_request(request)
        payload = auth.verify_token(token, verify_csrf=False)
        return {"username": payload.sub}
    except AuthXException:
        # Redirect to login with return URL
        raise RedirectToLogin(f"/login?next={request.url.path}")
```

### Protected Template Route

```python
from fastapi import Depends

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: dict = Depends(require_auth)
):
    csrf_token = request.cookies.get("csrf_access_token", "")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "csrf_token": csrf_token,  # Pass to template for forms
        }
    )
```

---

## CSRF Protection in Forms

When using cookie-based auth, **CSRF protection is essential** for form submissions.

### Include CSRF Token in Templates

```html
<form action="/submit" method="post">
    <!-- Hidden CSRF token field -->
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">

    <input type="text" name="data">
    <button type="submit">Submit</button>
</form>
```

### Handling Form Submissions

```python
@app.post("/submit")
async def submit_form(
    request: Request,
    user: dict = Depends(require_auth),
    data: str = Form(...),
    csrf_token: str = Form(...),  # CSRF validated automatically
):
    # Process form data
    return RedirectResponse(url="/dashboard", status_code=303)
```

### JavaScript AJAX Requests

For JavaScript requests, read the CSRF token from the cookie:

```javascript
function getCsrfToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrf_access_token='))
        ?.split('=')[1];
}

fetch('/api/action', {
    method: 'POST',
    credentials: 'include',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': getCsrfToken()
    },
    body: JSON.stringify({ data: 'value' })
});
```

---

## Complete Example

Here's a minimal complete example:

```python
from fastapi import Depends, FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from authx import AuthX, AuthXConfig
from authx.exceptions import AuthXException

app = FastAPI()
templates = Jinja2Templates(directory="templates")

config = AuthXConfig(
    JWT_SECRET_KEY="secret",
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_COOKIE_CSRF_PROTECT=True,
    JWT_CSRF_CHECK_FORM=True,
)
auth = AuthX(config=config)


# Simple user store
USERS = {"admin": "password123"}


class RedirectToLogin(Exception):
    pass


@app.exception_handler(RedirectToLogin)
async def handle_redirect(request, exc):
    return RedirectResponse("/login", status_code=303)


async def require_auth(request: Request):
    try:
        token = await auth.get_access_token_from_request(request)
        return auth.verify_token(token, verify_csrf=False)
    except AuthXException:
        raise RedirectToLogin()


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if USERS.get(username) != password:
        return RedirectResponse("/login?error=1", status_code=303)

    token = auth.create_access_token(uid=username)
    response = RedirectResponse("/dashboard", status_code=303)
    auth.set_access_cookies(token, response)
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(require_auth)):
    csrf = request.cookies.get("csrf_access_token", "")
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user.sub, "csrf_token": csrf}
    )


@app.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    auth.unset_cookies(response)
    return response
```

---

## Template Examples

### login.html

```html
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h1>Login</h1>
    <form method="post" action="/login">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
</body>
</html>
```

### dashboard.html

```html
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
    <h1>Welcome, {{ user }}!</h1>

    <form method="post" action="/logout">
        <button type="submit">Logout</button>
    </form>

    <!-- Example form with CSRF -->
    <form method="post" action="/action">
        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
        <button type="submit">Do Action</button>
    </form>
</body>
</html>
```

---

## Full Working Example

For a complete working example with styled templates, see:

- [jinja2_templates.py](https://github.com/yezz123/authx/blob/main/examples/examples/jinja2_templates.py)
- [Templates folder](https://github.com/yezz123/authx/tree/main/examples/examples/templates/jinja2)

Run the example:

```bash
cd examples/examples
python jinja2_templates.py
```

Then visit `http://localhost:8000` and login with `admin` / `admin123`.
