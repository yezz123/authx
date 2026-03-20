# WebSocket Authentication

AuthX provides built-in support for authenticating WebSocket connections. Since WebSockets don't support custom headers after the initial handshake, tokens are typically passed as query parameters or in the handshake headers.

## How It Works

1. Client connects to `/ws?token=<jwt>` or sends the `Authorization` header during handshake
2. AuthX extracts and verifies the token before accepting the connection
3. If the token is missing or invalid, an exception is raised and you can reject the connection

## Complete Example

```python
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from authx import AuthX, AuthXConfig, TokenPayload

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginRequest):
    """Get a token to use with WebSocket."""
    if data.username == "test" and data.password == "test":
        token = auth.create_access_token(uid=data.username)
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    payload: TokenPayload = Depends(auth._ws_auth_required),
):
    """Authenticated WebSocket endpoint."""
    await websocket.accept()
    await websocket.send_json({"message": f"Hello, {payload.sub}!"})

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"user": payload.sub, "echo": data})
    except WebSocketDisconnect:
        pass
```

## Connecting from a Client

### Query Parameter (Recommended)

The simplest approach -- pass the token in the URL:

=== "JavaScript"
    ```javascript
    const token = "eyJ...";
    const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

    ws.onmessage = (event) => {
      console.log(JSON.parse(event.data));
    };

    ws.onopen = () => {
      ws.send("Hello server!");
    };
    ```

=== "Python"
    ```python
    import asyncio
    import websockets

    async def main():
        token = "eyJ..."
        async with websockets.connect(f"ws://localhost:8000/ws?token={token}") as ws:
            print(await ws.recv())
            await ws.send("Hello server!")
            print(await ws.recv())

    asyncio.run(main())
    ```

### Authorization Header

Some WebSocket clients support sending headers during the handshake:

```python
import asyncio
import websockets

async def main():
    token = "eyJ..."
    headers = {"Authorization": f"Bearer {token}"}
    async with websockets.connect("ws://localhost:8000/ws", extra_headers=headers) as ws:
        print(await ws.recv())

asyncio.run(main())
```

!!! note "Browser Limitation"
    The browser `WebSocket` API does **not** support custom headers. Use query parameters for browser clients.

---

## Using the `WS_AUTH_REQUIRED` Property

For a cleaner syntax, use the `WS_AUTH_REQUIRED` dependency property:

```python
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    payload: TokenPayload = auth.WS_AUTH_REQUIRED,
):
    await websocket.accept()
    await websocket.send_json({"user": payload.sub})
```

---

## Handling Connection Rejection

If authentication fails, you should close the WebSocket with an appropriate code:

```python
from authx.exceptions import AuthXException

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        payload = await auth._ws_auth_required(websocket)
    except AuthXException:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    await websocket.accept()
    await websocket.send_json({"user": payload.sub})
```

---

## Token Lookup Order

The WebSocket auth dependency checks for tokens in this order:

1. **Query parameter** — `?token=<jwt>` (configurable via `JWT_QUERY_STRING_NAME`)
2. **Authorization header** — `Authorization: Bearer <jwt>` (configurable via `JWT_HEADER_NAME` / `JWT_HEADER_TYPE`)

The first token found is used. If neither is present, `MissingTokenError` is raised.

---

## With Scopes

Scope checking works the same way as with HTTP routes:

```python
@app.websocket("/ws/admin")
async def admin_ws(websocket: WebSocket):
    try:
        payload = await auth._ws_auth_required(websocket)
    except AuthXException:
        await websocket.close(code=4001)
        return

    if not payload.has_scopes("admin:*"):
        await websocket.close(code=4003, reason="Insufficient permissions")
        return

    await websocket.accept()
    await websocket.send_json({"admin": True, "user": payload.sub})
```

---

## With Token Blocklist

Revoked tokens are automatically rejected. If you have a blocklist callback registered, it is checked during WebSocket authentication:

```python
auth.set_token_blocklist(lambda token: token in REVOKED_TOKENS)

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    payload: TokenPayload = auth.WS_AUTH_REQUIRED,
):
    await websocket.accept()
    # If the token is revoked, the connection never reaches here
```

---

## Configuration Reference

| Setting | Default | Used For |
|---------|---------|----------|
| `JWT_QUERY_STRING_NAME` | `"token"` | Query parameter name for WebSocket token |
| `JWT_HEADER_NAME` | `"Authorization"` | Header name for handshake authentication |
| `JWT_HEADER_TYPE` | `"Bearer"` | Expected prefix in the Authorization header |

---

## Next Steps

- [Basic Usage](./basic-usage.md) - Getting started with AuthX
- [JWT Locations](./location.md) - Token transport for HTTP routes
- [Token Callbacks](../callbacks/token.md) - Setting up token blocklists
- [Scope Management](./scopes.md) - Fine-grained access control
