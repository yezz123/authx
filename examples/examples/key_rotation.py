from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from authx import AuthX, AuthXConfig

# Create a FastAPI app
app = FastAPI(title="AuthX Key Rotation Example")

# Configure AuthX with key rotation
# In production, load these from environment variables or a secrets manager
auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="new-secret-key-2026",
    JWT_PREVIOUS_SECRET_KEY="old-secret-key-2025",
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


# Sample user database
USERS = {
    "user1": {"password": "password1", "email": "user1@example.com"},
    "user2": {"password": "password2", "email": "user2@example.com"},
}


@app.post("/login")
def login(user: User):
    """Login endpoint - new tokens are always signed with the current key."""
    if user.username in USERS and USERS[user.username]["password"] == user.password:
        access_token = auth.create_access_token(user.username)
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/protected")
async def protected(request: Request):
    """Protected route - accepts tokens signed with current OR previous key."""
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token)
    return {
        "message": "Access granted",
        "username": payload.sub,
        "email": USERS.get(payload.sub, {}).get("email"),
    }


@app.get("/")
def read_root():
    """Public route."""
    return {
        "message": "Welcome to AuthX Key Rotation Example",
        "info": "Tokens signed with both the current and previous key are accepted.",
        "endpoints": {
            "login": "POST /login - Get an access token (signed with current key)",
            "protected": "GET /protected - Accepts tokens from current or previous key",
        },
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
