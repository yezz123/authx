"""Dual Token Location Example - Access Token in Header, Refresh Token in Cookie.

This example demonstrates a common and secure pattern for web applications:
- Access tokens (short-lived) are sent via Authorization header
- Refresh tokens (long-lived) are stored in HTTP-only cookies

Benefits of this approach:
- Access tokens in headers: Standard for APIs, works with any client, no CSRF concerns
- Refresh tokens in cookies: Secure storage, HTTP-only prevents XSS theft, automatic sending

Flow:
1. Login: Returns access_token in response body, sets refresh_token as HTTP-only cookie
2. API calls: Client sends access_token in Authorization header
3. Refresh: Client calls /refresh, refresh_token is sent automatically via cookie
4. Logout: Server clears the refresh_token cookie
"""

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

from authx import AuthX, AuthXConfig

# Create a FastAPI app
app = FastAPI(title="AuthX Dual Token Location Example")

# Configure AuthX for dual token locations
auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="your-secret-key",  # In production, use a secure key from environment variables
    # Enable both locations - we'll specify which to use per-endpoint
    JWT_TOKEN_LOCATION=["headers", "cookies"],
    # Header settings for access tokens
    JWT_HEADER_NAME="Authorization",
    JWT_HEADER_TYPE="Bearer",
    # Cookie settings for refresh tokens
    JWT_REFRESH_COOKIE_NAME="refresh_token_cookie",
    JWT_REFRESH_COOKIE_PATH="/",
    JWT_COOKIE_SECURE=False,  # Set to True in production (requires HTTPS)
    JWT_COOKIE_HTTP_ONLY=True,  # Prevent JavaScript access to refresh token
    JWT_COOKIE_SAMESITE="lax",  # Protect against CSRF
    JWT_COOKIE_CSRF_PROTECT=True,  # Enable CSRF protection for cookie-based refresh
    JWT_REFRESH_CSRF_COOKIE_NAME="csrf_refresh_token",
    JWT_REFRESH_CSRF_HEADER_NAME="X-CSRF-TOKEN",
)

# Initialize AuthX
auth = AuthX(config=auth_config)

# Register error handlers
auth.handle_errors(app)


# Define models
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Sample user database (in a real app, you would use a database)
USERS = {
    "user1": {"password": "password1", "email": "user1@example.com"},
    "user2": {"password": "password2", "email": "user2@example.com"},
}


@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, response: Response):
    """Login endpoint that:
    - Returns access_token in the response body (for client to store in memory)
    - Sets refresh_token as an HTTP-only cookie (for secure storage).
    """
    # Validate credentials
    if data.username not in USERS or USERS[data.username]["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create tokens
    access_token = auth.create_access_token(uid=data.username)
    refresh_token = auth.create_refresh_token(uid=data.username)

    # Set ONLY the refresh token in a cookie (with CSRF protection)
    # The access token is NOT stored in a cookie - it will be in client memory
    auth.set_refresh_cookies(refresh_token, response)

    # Return access token in response body
    # Client should store this in memory (not localStorage for XSS protection)
    return TokenResponse(access_token=access_token)


@app.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request):
    """Refresh endpoint that:
    - Reads refresh_token from the HTTP-only cookie (automatically sent by browser)
    - Validates the refresh token
    - Returns a new access_token in the response body.

    For POST requests with cookies, CSRF token must be included in X-CSRF-TOKEN header.
    """
    try:
        # Get refresh token from COOKIES only (not headers)
        # The locations parameter restricts where to look for the token
        refresh_token = await auth.get_refresh_token_from_request(
            request,
            locations=["cookies"],  # Only look in cookies
        )

        # Verify the refresh token (CSRF is verified automatically for cookies)
        payload = auth.verify_token(refresh_token, verify_type=True)

        # Create a new access token
        new_access_token = auth.create_access_token(uid=payload.sub)

        # Return in response body (client stores in memory)
        return TokenResponse(access_token=new_access_token)

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.get("/protected")
async def protected_route(request: Request):
    """Protected route that requires access_token in the Authorization header.

    Example request:
        curl -H "Authorization: Bearer <access_token>" http://localhost:8000/protected
    """
    try:
        # Get access token from HEADERS only (not cookies)
        access_token = await auth.get_access_token_from_request(
            request,
            locations=["headers"],  # Only look in headers
        )

        # Verify the access token
        # No CSRF verification needed for header-based tokens
        payload = auth.verify_token(access_token, verify_csrf=False)

        # Get user info
        username = payload.sub
        user_data = USERS.get(username, {})

        return {
            "message": "Access granted",
            "username": username,
            "email": user_data.get("email"),
            "token_location": access_token.location,
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.post("/protected-action")
async def protected_action(request: Request):
    """Protected POST route that requires access_token in the Authorization header.

    This demonstrates that even for POST requests, when using header-based auth,
    no CSRF token is needed (CSRF is only a concern for cookie-based auth).
    """
    try:
        # Get access token from HEADERS only
        access_token = await auth.get_access_token_from_request(
            request,
            locations=["headers"],
        )

        # Verify the access token (no CSRF for headers)
        payload = auth.verify_token(access_token, verify_csrf=False)

        return {
            "message": "Action performed successfully",
            "username": payload.sub,
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.post("/logout")
def logout(response: Response):
    """Logout endpoint that clears the refresh token cookie.

    The access token (stored in client memory) will naturally be cleared
    when the client discards it or the page is refreshed.
    """
    # Only unset refresh cookies (access token is in client memory, not managed by server)
    auth.unset_refresh_cookies(response)
    return {"message": "Successfully logged out"}


@app.get("/")
def read_root():
    """Public route with API documentation."""
    return {
        "message": "AuthX Dual Token Location Example",
        "description": "Access tokens in headers, refresh tokens in cookies",
        "flow": {
            "1_login": "POST /login - Returns access_token in body, sets refresh_token cookie",
            "2_api_call": "GET /protected - Send access_token in Authorization header",
            "3_refresh": "POST /refresh - Refresh token sent via cookie, returns new access_token",
            "4_logout": "POST /logout - Clears refresh_token cookie",
        },
        "example_requests": {
            "login": 'curl -X POST -H "Content-Type: application/json" -d \'{"username":"user1","password":"password1"}\' http://localhost:8000/login',
            "protected": 'curl -H "Authorization: Bearer <access_token>" http://localhost:8000/protected',
            "refresh": 'curl -X POST -b "refresh_token_cookie=<token>" -H "X-CSRF-TOKEN: <csrf_token>" http://localhost:8000/refresh',
            "logout": "curl -X POST http://localhost:8000/logout",
        },
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
