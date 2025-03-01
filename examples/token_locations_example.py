from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

from authx import AuthX, AuthXConfig

# Create a FastAPI app
app = FastAPI(title="AuthX Token Locations Example")

# Configure AuthX
auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="your-secret-key",  # In production, use a secure key and store it in environment variables
    # Configure token locations
    JWT_TOKEN_LOCATION=["headers", "cookies", "json", "query"],
    # Header settings
    JWT_HEADER_TYPE="Bearer",
    # Cookie settings
    JWT_ACCESS_COOKIE_NAME="access_token_cookie",
    JWT_REFRESH_COOKIE_NAME="refresh_token_cookie",
    JWT_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    JWT_COOKIE_CSRF_PROTECT=False,  # Disable CSRF protection for testing
    JWT_ACCESS_CSRF_COOKIE_NAME="csrf_access_token",
    JWT_REFRESH_CSRF_COOKIE_NAME="csrf_refresh_token",
    JWT_ACCESS_CSRF_HEADER_NAME="X-CSRF-TOKEN-Access",
    JWT_REFRESH_CSRF_HEADER_NAME="X-CSRF-TOKEN-Refresh",
    # JSON body settings
    JWT_JSON_KEY="access_token",
    JWT_REFRESH_JSON_KEY="refresh_token",
    # Query string settings
    JWT_QUERY_STRING_NAME="token",
)

# Initialize AuthX
auth = AuthX(config=auth_config)

# Register error handlers
auth.handle_errors(app)


# Define models
class User(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenBody(BaseModel):
    access_token: str


# Sample user database (in a real app, you would use a database)
USERS = {
    "user1": {"password": "password1", "email": "user1@example.com"},
    "user2": {"password": "password2", "email": "user2@example.com"},
}


@app.post("/login")
def login(user: User, response: Response):
    """Login endpoint that validates credentials and returns tokens."""
    # Check if user exists and password is correct
    if user.username in USERS and USERS[user.username]["password"] == user.password:
        # Create access and refresh tokens
        access_token = auth.create_access_token(user.username)
        refresh_token = auth.create_refresh_token(user.username)

        # Set tokens in cookies
        auth.set_access_cookies(response, access_token)
        auth.set_refresh_cookies(response, refresh_token)

        # Return tokens in response body
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "message": "Tokens are set in cookies and returned in the response body",
        }

    # Return error if credentials are invalid
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/logout")
def logout(response: Response):
    """Logout endpoint that clears the cookies."""
    auth.unset_jwt_cookies(response)
    return {"message": "Successfully logged out"}


@app.get("/protected")
async def protected_route(request: Request):
    """Protected route that requires a valid access token from any location."""
    try:
        # Get and verify the token from the request
        token = await auth.get_token_from_request(request)
        payload = auth.verify_token(token)

        # Get the token location
        token_location = auth.get_token_location(request)

        return {"message": "Access granted", "username": payload.sub, "token_location": token_location}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.post("/protected-post")
async def protected_post_route(request: Request, token_body: TokenBody = None):
    """Protected route that requires a valid access token from any location."""
    try:
        # Get and verify the token from the request
        token = await auth.get_token_from_request(request)
        payload = auth.verify_token(token)

        # Get the token location
        token_location = auth.get_token_location(request)

        return {"message": "Access granted", "username": payload.sub, "token_location": token_location}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.get("/protected/headers")
async def protected_headers(request: Request):
    """Protected route that expects the token in the Authorization header."""
    try:
        # Get and verify the token from the request
        token = await auth.get_token_from_request(request)
        payload = auth.verify_token(token)

        # Get the token location
        token_location = auth.get_token_location(request)

        return {
            "message": "Access granted via Authorization header",
            "username": payload.sub,
            "token_location": token_location,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.get("/protected/cookies")
async def protected_cookies(request: Request):
    """Protected route that expects the token in cookies."""
    try:
        # Get and verify the token from the request
        token = await auth.get_token_from_request(request)
        payload = auth.verify_token(token)

        # Get the token location
        token_location = auth.get_token_location(request)

        return {"message": "Access granted via cookies", "username": payload.sub, "token_location": token_location}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.post("/protected/json")
async def protected_json(request: Request, token_body: TokenBody = None):
    """Protected route that expects the token in the JSON body."""
    try:
        # Get and verify the token from the request
        token = await auth.get_token_from_request(request)
        payload = auth.verify_token(token)

        # Get the token location
        token_location = auth.get_token_location(request)

        return {"message": "Access granted via JSON body", "username": payload.sub, "token_location": token_location}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.get("/protected/query")
async def protected_query(request: Request):
    """Protected route that expects the token in the query string."""
    try:
        # Get and verify the token from the request
        token = await auth.get_token_from_request(request)
        payload = auth.verify_token(token)

        # Get the token location
        token_location = auth.get_token_location(request)

        return {"message": "Access granted via query string", "username": payload.sub, "token_location": token_location}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.get("/")
def read_root():
    """Public route that doesn't require authentication."""
    return {
        "message": "Welcome to AuthX Token Locations Example",
        "endpoints": {
            "login": "POST /login - Get tokens in cookies and response body",
            "logout": "POST /logout - Clear the cookies",
            "protected": "GET /protected - Access with token from any location",
            "protected-post": "POST /protected-post - Access with token from any location",
            "protected/headers": "GET /protected/headers - Access with token in Authorization header",
            "protected/cookies": "GET /protected/cookies - Access with token in cookies",
            "protected/json": "POST /protected/json - Access with token in JSON body",
            "protected/query": "GET /protected/query?token=<your_token> - Access with token in query string",
        },
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
