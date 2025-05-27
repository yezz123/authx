from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from authx import AuthX, AuthXConfig

# Create a FastAPI app
app = FastAPI(title="AuthX Basic Authentication Example")

# Configure AuthX
auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="your-secret-key",  # In production, use a secure key and store it in environment variables
    JWT_TOKEN_LOCATION=["headers"],  # Accept tokens in headers
    JWT_HEADER_TYPE="Bearer",  # Use Bearer authentication
)

# Initialize AuthX
auth = AuthX(config=auth_config)

# Register error handlers
auth.handle_errors(app)


# Define a user model for login
class User(BaseModel):
    username: str
    password: str


# Sample user database (in a real app, you would use a database)
USERS = {
    "user1": {"password": "password1", "email": "user1@example.com"},
    "user2": {"password": "password2", "email": "user2@example.com"},
}


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


@app.get("/protected")
async def protected_route(request: Request):
    """Protected route that requires a valid access token."""
    try:
        # Get the token from the request
        token = await auth.get_access_token_from_request(request)

        # Verify the token
        payload = auth.verify_token(token)

        # Get the username from the token subject
        username = payload.sub

        # Return user information
        return {
            "message": "You have access to this protected resource",
            "username": username,
            "email": USERS.get(username, {}).get("email"),
        }
    except Exception as e:
        # Print the error for debugging
        print(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e)) from e


@app.get("/")
def read_root():
    """Public route that doesn't require authentication."""
    return {
        "message": "Welcome to AuthX Basic Authentication Example",
        "endpoints": {
            "login": "POST /login - Get an access token",
            "protected": "GET /protected - Access protected resource (requires token)",
        },
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
