from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from authx import AuthX, AuthXConfig

# Create a FastAPI app
app = FastAPI(title="AuthX Token Blocklist Example")

# Configure AuthX
auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="your-secret-key",  # In production, use a secure key and store it in environment variables
    JWT_TOKEN_LOCATION=["headers"],
    JWT_HEADER_TYPE="Bearer",
)

# Initialize AuthX
auth = AuthX(config=auth_config)

# Register error handlers
auth.handle_errors(app)


# Define models
class User(BaseModel):
    username: str
    password: str


# Sample user database (in a real app, you would use a database)
USERS = {
    "user1": {"password": "password1", "email": "user1@example.com"},
    "user2": {"password": "password2", "email": "user2@example.com"},
}

# In-memory blocklist (in a real app, you would use Redis or a database)
TOKEN_BLOCKLIST: set[str] = set()


# Custom callback for checking if a token is in the blocklist
def token_blocklist_check(jti: str) -> bool:
    """Check if a token is in the blocklist.
    Returns True if the token is blocklisted (revoked).
    """
    return jti in TOKEN_BLOCKLIST


# Register the blocklist callback
auth.token_blocklist_callback = token_blocklist_check


@app.post("/login")
def login(user: User):
    """Login endpoint that validates credentials and returns an access token."""
    # Check if user exists and password is correct
    if user.username in USERS and USERS[user.username]["password"] == user.password:
        # Create an access token with the username as the subject
        access_token = auth.create_access_token(user.username)
        return {"access_token": access_token, "token_type": "bearer"}

    # Return error if credentials are invalid
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/logout")
async def logout(request: Request):
    """Logout endpoint that adds the current token to the blocklist."""
    try:
        # Get the token from the request
        token = await auth.get_access_token_from_request(request)

        # Verify the token
        payload = auth.verify_token(token)

        # Add the token's JTI (JWT ID) to the blocklist
        TOKEN_BLOCKLIST.add(payload.jti)

        return {"message": "Successfully logged out"}
    except Exception as e:
        print(f"Logout error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.get("/blocklist")
def get_blocklist():
    """Get the current blocklist (for demonstration purposes)."""
    return {"blocklist": list(TOKEN_BLOCKLIST)}


@app.get("/protected")
async def protected_route(request: Request):
    """Protected route that requires a valid access token."""
    try:
        # Get the token from the request
        token = await auth.get_access_token_from_request(request)

        # Verify the token (this will also check if it's blocklisted)
        payload = auth.verify_token(token)
        if payload.jti in list(TOKEN_BLOCKLIST):
            raise HTTPException(status_code=401, detail="token blocklisted")

        # Get the username from the token subject
        username = payload.sub

        # Return user information
        return {
            "message": "You have access to this protected resource",
            "username": username,
            "email": USERS.get(username, {}).get("email"),
            "token_jti": payload.jti,
        }
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.get("/")
def read_root():
    """Public route that doesn't require authentication."""
    return {
        "message": "Welcome to AuthX Token Blocklist Example",
        "endpoints": {
            "login": "POST /login - Get an access token",
            "logout": "POST /logout - Revoke the current token",
            "blocklist": "GET /blocklist - View the current blocklist",
            "protected": "GET /protected - Access protected resource (requires token)",
        },
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
