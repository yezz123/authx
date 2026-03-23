# Session Management

AuthX provides full session tracking with device information, IP tracking, and the ability to list and revoke sessions across devices. Sessions are managed via a pluggable `SessionStore` backend.

## How It Works

1. User logs in, you call `auth.create_session(uid, request)` to record the session
2. The session captures IP address, User-Agent, and optional device metadata
3. Users can list their active sessions and revoke individual ones or all at once
4. Admins can revoke all sessions for a user (e.g., on password change)

## Complete Example

```python
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from authx import AuthX, AuthXConfig, SessionInfo
from authx._internal._session import InMemorySessionStore

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="a]V&F*jk2s$5ghT!qR@pN8xLm3wY+bZ",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)
auth.set_session_store(InMemorySessionStore())


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(data: LoginRequest, request: Request):
    """Login and create a tracked session."""
    if data.username == "test" and data.password == "test":
        session = await auth.create_session(uid=data.username, request=request)
        token = auth.create_access_token(
            uid=data.username,
            data={"session_id": session.session_id},
        )
        return {"access_token": token, "session_id": session.session_id}
    raise HTTPException(401, detail="Invalid credentials")


@app.get("/sessions")
async def list_sessions(request: Request):
    """List all active sessions for the current user."""
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token)
    sessions = await auth.list_sessions(payload.sub)
    return {"sessions": [s.model_dump() for s in sessions]}


@app.post("/sessions/{session_id}/revoke")
async def revoke_session(session_id: str, request: Request):
    """Revoke a specific session."""
    token = await auth.get_access_token_from_request(request)
    auth.verify_token(token)
    await auth.revoke_session(session_id)
    return {"message": "Session revoked"}


@app.post("/sessions/revoke-all")
async def revoke_all(request: Request):
    """Revoke all sessions for the current user."""
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token)
    await auth.revoke_all_sessions(payload.sub)
    return {"message": "All sessions revoked"}
```

---

## Setting Up a Session Store

Register a session store when initializing your app:

```python
from authx._internal._session import InMemorySessionStore

auth.set_session_store(InMemorySessionStore())
```

For production, implement the `SessionStoreProtocol` with your database:

```python
class RedisSessionStore:
    async def create(self, session: SessionInfo) -> None:
        await redis.set(f"session:{session.session_id}", session.model_dump_json())

    async def get(self, session_id: str) -> SessionInfo | None:
        data = await redis.get(f"session:{session_id}")
        return SessionInfo.model_validate_json(data) if data else None

    async def update(self, session_id: str, **kwargs) -> None:
        session = await self.get(session_id)
        if session:
            for k, v in kwargs.items():
                setattr(session, k, v)
            await redis.set(f"session:{session.session_id}", session.model_dump_json())

    async def delete(self, session_id: str) -> None:
        await redis.delete(f"session:{session_id}")

    async def list_by_user(self, uid: str) -> list[SessionInfo]:
        # Implement with Redis sorted sets or secondary index
        ...

    async def delete_all_by_user(self, uid: str) -> None:
        for session in await self.list_by_user(uid):
            await self.delete(session.session_id)
```

---

## SessionInfo Model

`SessionInfo` is a Pydantic model usable as a FastAPI `response_model`:

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | `str` | Unique session identifier (auto-generated UUID) |
| `uid` | `str` | User identifier |
| `created_at` | `datetime` | When the session was created |
| `last_active` | `datetime` | Last activity timestamp |
| `ip_address` | `str` | Client IP address (from request) |
| `user_agent` | `str` | Browser/client User-Agent string |
| `device_info` | `dict` | Optional additional device metadata |
| `is_active` | `bool` | Whether the session is active |

---

## API Reference

### `auth.set_session_store(store)`

Register a session storage backend.

### `await auth.create_session(uid, request=None, device_info=None)`

Create and persist a new session. Extracts IP and User-Agent from the request if provided.

### `await auth.list_sessions(uid)`

List all active sessions for a user.

### `await auth.revoke_session(session_id)`

Revoke a single session by ID.

### `await auth.revoke_all_sessions(uid)`

Revoke all sessions for a user. Useful for "log out everywhere" or after a password change.

### `await auth.get_session(session_id)`

Retrieve a single session by ID.

---

## Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `JWT_SESSION_TRACKING` | `bool` | `False` | Enable session tracking (opt-in) |
| `JWT_SESSION_UPDATE_LAST_ACTIVE` | `bool` | `True` | Auto-update `last_active` on each auth check |

---

## Next Steps

- [Basic Usage](./basic-usage.md) - Getting started with AuthX
- [Rate Limiting](./rate-limiting.md) - Protect endpoints from abuse
- [Token Callbacks](../callbacks/token.md) - Token blocklist for revocation
- [Key Rotation](./key-rotation.md) - Zero-downtime key rotation
