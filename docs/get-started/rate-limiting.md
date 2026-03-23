# Rate Limiting

AuthX provides built-in rate limiting to protect your auth endpoints from brute-force attacks. It includes a standalone `RateLimiter` dependency and an integrated `auth.rate_limited()` method that combines rate limiting with token verification.

## Standalone RateLimiter

Use `RateLimiter` as a FastAPI dependency on any route:

```python
from fastapi import FastAPI, Depends
from authx import RateLimiter

app = FastAPI()

limiter = RateLimiter(max_requests=10, window=60)

@app.get("/api", dependencies=[Depends(limiter)])
async def api_route():
    return {"message": "You're within the limit"}
```

When the limit is exceeded, a `429 Too Many Requests` response is returned with a `Retry-After` header.

## Complete Example

```python
from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel
from authx import AuthX, AuthXConfig, RateLimiter

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="a]V&F*jk2s$5ghT!qR@pN8xLm3wY+bZ",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)

login_limiter = RateLimiter(max_requests=5, window=300)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login", dependencies=[Depends(login_limiter)])
def login(data: LoginRequest):
    """Login with rate limiting: 5 attempts per 5 minutes."""
    if data.username == "test" and data.password == "test":
        token = auth.create_access_token(uid=data.username)
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")


@app.get("/protected")
async def protected(request: Request):
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token)
    return {"user": payload.sub}
```

---

## Integrated Rate Limiting + Auth

Use `auth.rate_limited()` to combine rate limiting with token verification in a single dependency:

```python
@app.get("/api")
async def api_route(request: Request):
    payload = await auth.rate_limited(max_requests=20, window=60)(request)
    return {"user": payload.sub}
```

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_requests` | `int` | `10` | Maximum requests allowed within the window |
| `window` | `int` | `60` | Time window in seconds |
| `backend` | `RateLimitBackend` | `InMemoryBackend` | Storage backend (pluggable) |
| `key_func` | `Callable` | Client IP | Function to extract rate limit key from request |

---

## Custom Key Functions

By default, rate limiting is keyed by client IP. You can customize this:

```python
def by_api_key(request: Request) -> str:
    return f"apikey:{request.headers.get('X-API-Key', 'anonymous')}"

limiter = RateLimiter(max_requests=100, window=3600, key_func=by_api_key)
```

---

## Custom Backends

The `InMemoryBackend` works for single-process deployments. For multi-worker setups, implement the `RateLimitBackend` protocol:

```python
class RedisBackend:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def increment(self, key: str, window: int) -> int:
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        result = await pipe.execute()
        return result[0]

    async def reset(self, key: str) -> None:
        await self.redis.delete(key)

limiter = RateLimiter(max_requests=100, window=60, backend=RedisBackend(redis))
```

---

## Error Response

When the rate limit is exceeded, AuthX returns:

```json
{
    "message": "Rate limit exceeded. Retry after 60 seconds.",
    "error_type": "RateLimitExceeded",
    "retry_after": 60
}
```

With HTTP status `429` and a `Retry-After: 60` header.

---

## Next Steps

- [Basic Usage](./basic-usage.md) - Getting started with AuthX
- [WebSocket Auth](./websocket.md) - Authenticating WebSocket connections
- [Session Management](./sessions.md) - Track and manage user sessions
