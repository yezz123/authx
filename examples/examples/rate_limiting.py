from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

from authx import AuthX, AuthXConfig, RateLimiter

app = FastAPI(title="AuthX Rate Limiting Example")

auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="a]V&F*jk2s$5ghT!qR@pN8xLm3wY+bZ",
    JWT_TOKEN_LOCATION=["headers"],
    JWT_HEADER_TYPE="Bearer",
)

auth = AuthX(config=auth_config)
auth.handle_errors(app)

login_limiter = RateLimiter(max_requests=5, window=300)
api_limiter = RateLimiter(max_requests=30, window=60)


class User(BaseModel):
    username: str
    password: str


USERS = {
    "user1": {"password": "password1"},
    "user2": {"password": "password2"},
}


@app.post("/login", dependencies=[Depends(login_limiter)])
def login(user: User):
    """Login with rate limiting: 5 attempts per 5 minutes."""
    if user.username in USERS and USERS[user.username]["password"] == user.password:
        access_token = auth.create_access_token(user.username)
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/protected", dependencies=[Depends(api_limiter)])
async def protected(request: Request):
    """Protected route with API rate limiting: 30 requests per minute."""
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token)
    return {"message": "Access granted", "username": payload.sub}


@app.get("/")
def read_root():
    """Public route."""
    return {
        "message": "Welcome to AuthX Rate Limiting Example",
        "endpoints": {
            "login": "POST /login - Login (5 attempts per 5 min)",
            "protected": "GET /protected - API endpoint (30 req/min)",
        },
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
