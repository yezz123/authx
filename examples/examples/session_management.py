from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from authx import AuthX, AuthXConfig
from authx._internal._session import InMemorySessionStore

app = FastAPI(title="AuthX Session Management Example")

auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="a]V&F*jk2s$5ghT!qR@pN8xLm3wY+bZ",
    JWT_TOKEN_LOCATION=["headers"],
    JWT_HEADER_TYPE="Bearer",
)

auth = AuthX(config=auth_config)
auth.handle_errors(app)
auth.set_session_store(InMemorySessionStore())


class User(BaseModel):
    username: str
    password: str


USERS = {
    "user1": {"password": "password1"},
    "user2": {"password": "password2"},
}


@app.post("/login")
async def login(user: User, request: Request):
    """Login and create a tracked session."""
    if user.username in USERS and USERS[user.username]["password"] == user.password:
        session = await auth.create_session(uid=user.username, request=request)
        access_token = auth.create_access_token(
            user.username,
            data={"session_id": session.session_id},
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "session_id": session.session_id,
        }
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/sessions")
async def list_sessions(request: Request):
    """List all active sessions for the current user."""
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token)
    sessions = await auth.list_sessions(payload.sub)
    return {"sessions": [s.model_dump(mode="json") for s in sessions]}


@app.post("/sessions/{session_id}/revoke")
async def revoke_session(session_id: str, request: Request):
    """Revoke a specific session."""
    token = await auth.get_access_token_from_request(request)
    auth.verify_token(token)
    await auth.revoke_session(session_id)
    return {"message": f"Session {session_id} revoked"}


@app.post("/sessions/revoke-all")
async def revoke_all_sessions(request: Request):
    """Revoke all sessions for the current user (logout everywhere)."""
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token)
    await auth.revoke_all_sessions(payload.sub)
    return {"message": "All sessions revoked"}


@app.get("/protected")
async def protected(request: Request):
    """Protected route."""
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token)
    return {"message": "Access granted", "username": payload.sub}


@app.get("/")
def read_root():
    """Public route."""
    return {
        "message": "Welcome to AuthX Session Management Example",
        "endpoints": {
            "login": "POST /login - Login and create session",
            "sessions": "GET /sessions - List active sessions",
            "revoke": "POST /sessions/{id}/revoke - Revoke a session",
            "revoke_all": "POST /sessions/revoke-all - Revoke all sessions",
            "protected": "GET /protected - Protected resource",
        },
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
