from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from authx import AuthX, AuthXConfig
from authx.exceptions import AuthXException

# Create a FastAPI app
app = FastAPI(title="AuthX WebSocket Auth Example")

# Configure AuthX
auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="your-secret-key",
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
    "user1": {"password": "password1"},
    "user2": {"password": "password2"},
}


@app.post("/login")
def login(user: User):
    """Login endpoint to get a token for WebSocket authentication."""
    if user.username in USERS and USERS[user.username]["password"] == user.password:
        access_token = auth.create_access_token(user.username)
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Authenticated WebSocket using dependency-style auth.

    Connect with: ws://localhost:8000/ws?token=<your-jwt>
    """
    try:
        payload = await auth._ws_auth_required(websocket)
    except AuthXException:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    await websocket.accept()
    await websocket.send_json({"message": f"Hello, {payload.sub}!", "type": "connected"})

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"user": payload.sub, "echo": data, "type": "message"})
    except WebSocketDisconnect:
        pass


@app.websocket("/ws/manual")
async def websocket_manual_auth(websocket: WebSocket):
    """WebSocket with manual authentication and error handling.

    Connect with: ws://localhost:8000/ws/manual?token=<your-jwt>
    """
    try:
        payload = await auth._ws_auth_required(websocket)
    except AuthXException:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    await websocket.accept()
    await websocket.send_json({"message": f"Hello, {payload.sub}!", "type": "connected"})

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"user": payload.sub, "echo": data, "type": "message"})
    except WebSocketDisconnect:
        pass


@app.get("/")
def read_root():
    """Public route."""
    return {
        "message": "Welcome to AuthX WebSocket Auth Example",
        "endpoints": {
            "login": "POST /login - Get a JWT token",
            "ws": "WS /ws?token=<jwt> - Authenticated WebSocket (dependency injection)",
            "ws_manual": "WS /ws/manual?token=<jwt> - Authenticated WebSocket (manual auth)",
        },
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
