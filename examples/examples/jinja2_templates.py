"""AuthX with Jinja2 Template Engine Example.

This example demonstrates how to use AuthX with Jinja2 templates for
server-side rendered (SSR) web applications with a traditional login flow.

Flow:
    login.html --> POST /login --> dashboard.html --> POST /logout --> login.html
                                       |
                                       +--> process.html (/route1, /route2, etc.)

Key concepts:
- Cookie-based authentication (tokens stored in HTTP-only cookies)
- Redirect-based flow (not JSON responses)
- CSRF protection for form submissions
- Protected routes that redirect to login on auth failure
"""

import os
from pathlib import Path
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from authx import AuthX, AuthXConfig
from authx.exceptions import AuthXException

# Create FastAPI app
app = FastAPI(title="AuthX Jinja2 Templates Example")

# Setup templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates" / "jinja2"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Configure AuthX for cookie-based authentication
auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="your-secret-key",  # Use env var in production
    # Cookie-based auth for SSR applications
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_ACCESS_COOKIE_NAME="access_token_cookie",
    JWT_REFRESH_COOKIE_NAME="refresh_token_cookie",
    # Cookie security settings
    JWT_COOKIE_SECURE=False,  # Set True in production (HTTPS)
    JWT_COOKIE_HTTP_ONLY=True,  # Prevent JavaScript access
    JWT_COOKIE_SAMESITE="lax",  # CSRF protection
    # Enable CSRF protection for form submissions
    JWT_COOKIE_CSRF_PROTECT=True,
    JWT_CSRF_IN_COOKIES=True,
    JWT_ACCESS_CSRF_COOKIE_NAME="csrf_access_token",
    JWT_ACCESS_CSRF_HEADER_NAME="X-CSRF-TOKEN",
    JWT_CSRF_CHECK_FORM=True,  # Check CSRF in form data
    JWT_ACCESS_CSRF_FIELD_NAME="csrf_token",  # Form field name for CSRF
)

auth = AuthX(config=auth_config)
auth.handle_errors(app)

# Sample user database
USERS = {
    "admin": {"password": "admin123", "name": "Administrator", "role": "admin"},
    "user": {"password": "user123", "name": "Regular User", "role": "user"},
}


async def get_current_user_optional(request: Request) -> Optional[dict]:
    """Get current user from cookie, return None if not authenticated."""
    try:
        token = await auth.get_access_token_from_request(request, locations=["cookies"])
        payload = auth.verify_token(token, verify_csrf=False)  # Don't verify CSRF on GET
        username = payload.sub
        if username in USERS:
            return {"username": username, **USERS[username]}
    except AuthXException:
        pass
    return None


class RedirectToLogin(Exception):
    """Custom exception to trigger redirect to login page."""

    def __init__(self, redirect_url: str = "/login"):
        self.redirect_url = redirect_url


async def require_auth(request: Request) -> dict:
    """Dependency that requires authentication, redirects to login if not authenticated."""
    user = await get_current_user_optional(request)
    if user is None:
        # Store the original URL to redirect back after login
        redirect_url = f"/login?next={request.url.path}"
        raise RedirectToLogin(redirect_url)
    return user


# Type alias for authenticated user dependency (avoids B008 linter warning)
AuthUser = Annotated[dict, Depends(require_auth)]


@app.exception_handler(RedirectToLogin)
async def redirect_to_login_handler(request: Request, exc: RedirectToLogin):
    """Handle RedirectToLogin exception by redirecting to login page."""
    return RedirectResponse(url=exc.redirect_url, status_code=303)


# ============================================================================
# PUBLIC ROUTES
# ============================================================================


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - public, shows login link or dashboard link based on auth status."""
    user = await get_current_user_optional(request)
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "user": user},
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None, next: str = "/dashboard"):
    """Render login form."""
    # If already logged in, redirect to dashboard
    user = await get_current_user_optional(request)
    if user:
        return RedirectResponse(url=next, status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error, "next": next},
    )


@app.post("/login")
async def login_submit(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/dashboard"),
):
    """Handle login form submission."""
    # Validate credentials
    if username not in USERS or USERS[username]["password"] != password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password", "next": next},
            status_code=401,
        )

    # Create tokens
    access_token = auth.create_access_token(uid=username)
    refresh_token = auth.create_refresh_token(uid=username)

    # Create redirect response
    redirect = RedirectResponse(url=next, status_code=303)

    # Set cookies on the redirect response
    auth.set_access_cookies(access_token, redirect)
    auth.set_refresh_cookies(refresh_token, redirect)

    return redirect


@app.post("/logout")
async def logout(request: Request):
    """Handle logout - clear cookies and redirect to login."""
    response = RedirectResponse(url="/login", status_code=303)
    auth.unset_cookies(response)
    return response


# ============================================================================
# PROTECTED ROUTES - Require authentication
# ============================================================================


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: AuthUser):
    """Protected dashboard page."""
    # Get CSRF token for forms on this page
    csrf_token = request.cookies.get("csrf_access_token", "")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "csrf_token": csrf_token,
        },
    )


@app.get("/process", response_class=HTMLResponse)
async def process_page(request: Request, user: AuthUser):
    """Protected process page with sub-routes."""
    csrf_token = request.cookies.get("csrf_access_token", "")

    return templates.TemplateResponse(
        "process.html",
        {
            "request": request,
            "user": user,
            "csrf_token": csrf_token,
            "current_route": "process",
        },
    )


@app.get("/route1", response_class=HTMLResponse)
async def route1(request: Request, user: AuthUser):
    """Protected route 1."""
    csrf_token = request.cookies.get("csrf_access_token", "")

    return templates.TemplateResponse(
        "process.html",
        {
            "request": request,
            "user": user,
            "csrf_token": csrf_token,
            "current_route": "route1",
            "message": "Welcome to Route 1 - Data Processing",
        },
    )


@app.get("/route2", response_class=HTMLResponse)
async def route2(request: Request, user: AuthUser):
    """Protected route 2."""
    csrf_token = request.cookies.get("csrf_access_token", "")

    return templates.TemplateResponse(
        "process.html",
        {
            "request": request,
            "user": user,
            "csrf_token": csrf_token,
            "current_route": "route2",
            "message": "Welcome to Route 2 - Reports",
        },
    )


@app.get("/route3", response_class=HTMLResponse)
async def route3(request: Request, user: AuthUser):
    """Protected route 3."""
    csrf_token = request.cookies.get("csrf_access_token", "")

    return templates.TemplateResponse(
        "process.html",
        {
            "request": request,
            "user": user,
            "csrf_token": csrf_token,
            "current_route": "route3",
            "message": "Welcome to Route 3 - Settings",
        },
    )


@app.get("/route4", response_class=HTMLResponse)
async def route4(request: Request, user: AuthUser):
    """Protected route 4."""
    csrf_token = request.cookies.get("csrf_access_token", "")

    return templates.TemplateResponse(
        "process.html",
        {
            "request": request,
            "user": user,
            "csrf_token": csrf_token,
            "current_route": "route4",
            "message": "Welcome to Route 4 - Analytics",
        },
    )


# ============================================================================
# PROTECTED FORM SUBMISSION (demonstrates CSRF protection)
# ============================================================================


@app.post("/process/action", response_class=HTMLResponse)
async def process_action(
    request: Request,
    user: AuthUser,
    action: str = Form(...),
    csrf_token: str = Form(...),  # CSRF token from form
):
    """Handle a protected form submission with CSRF validation."""
    # The CSRF token is validated automatically by AuthX when JWT_CSRF_CHECK_FORM=True
    # For manual validation, you would verify it matches the cookie

    csrf_token_cookie = request.cookies.get("csrf_access_token", "")

    return templates.TemplateResponse(
        "process.html",
        {
            "request": request,
            "user": user,
            "csrf_token": csrf_token_cookie,
            "current_route": "process",
            "message": f"Action '{action}' completed successfully!",
        },
    )


if __name__ == "__main__":
    import uvicorn

    # Ensure templates directory exists
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on http://localhost:{port}")
    print(f"Templates directory: {TEMPLATES_DIR}")
    print("\nTest credentials:")
    print("  Username: admin, Password: admin123")
    print("  Username: user, Password: user123")

    uvicorn.run(app, host="0.0.0.0", port=port)
