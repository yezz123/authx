# Token Blocklist

When a user logs out, you need to invalidate their token. Since JWTs are stateless, you need a blocklist to track revoked tokens.

## Complete Example

```python
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig, RequestToken, TokenPayload

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)

# Simple in-memory blocklist (use Redis/database in production)
BLOCKLIST: set[str] = set()


@auth.set_callback_token_blocklist
def is_token_revoked(token: str) -> bool:
    """Return True if token is revoked."""
    return token in BLOCKLIST


@app.post("/login")
def login(username: str, password: str):
    if username == "test" and password == "test":
        token = auth.create_access_token(uid=username)
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")


@app.post("/logout", dependencies=[Depends(auth.access_token_required)])
async def logout(request):
    """Add current token to blocklist."""
    token = await auth.get_access_token_from_request(request)
    BLOCKLIST.add(token.token)
    return {"message": "Logged out"}


@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Access granted"}
```

## How It Works

### 1. Define the Blocklist Callback

Create a function that checks if a token is revoked:

```python
@auth.set_callback_token_blocklist
def is_token_revoked(token: str) -> bool:
    """Return True if token is revoked, False otherwise."""
    return token in BLOCKLIST
```

This callback runs automatically whenever a protected route validates a token.

### 2. Add Tokens to Blocklist on Logout

```python
@app.post("/logout", dependencies=[Depends(auth.access_token_required)])
async def logout(request):
    token = await auth.get_access_token_from_request(request)
    BLOCKLIST.add(token.token)
    return {"message": "Logged out"}
```

## Testing

```bash
# 1. Login
curl -X POST "http://localhost:8000/login?username=test&password=test"
# {"access_token": "eyJ..."}

# 2. Access protected route - WORKS
curl -H "Authorization: Bearer <token>" http://localhost:8000/protected
# {"message": "Access granted"}

# 3. Logout
curl -X POST -H "Authorization: Bearer <token>" http://localhost:8000/logout
# {"message": "Logged out"}

# 4. Try to access protected route again - FAILS
curl -H "Authorization: Bearer <token>" http://localhost:8000/protected
# {"message": "Invalid token", "error_type": "RevokedTokenError"}
```

## Production: Using a Database

For production, store revoked tokens in a database. Here's an example with SQLAlchemy:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
from authx import AuthX, AuthXConfig, TokenPayload

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)

# Database setup
Base = declarative_base()
engine = create_engine("sqlite:///./tokens.db")
SessionLocal = sessionmaker(bind=engine)


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"
    token = Column(String, primary_key=True)
    revoked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)


@auth.set_callback_token_blocklist
def is_token_revoked(token: str) -> bool:
    with SessionLocal() as db:
        return db.query(RevokedToken).filter_by(token=token).first() is not None


@app.post("/login")
def login(username: str, password: str):
    if username == "test" and password == "test":
        return {"access_token": auth.create_access_token(uid=username)}
    raise HTTPException(401, detail="Invalid credentials")


@app.post("/logout", dependencies=[Depends(auth.access_token_required)])
async def logout(request):
    token = await auth.get_access_token_from_request(request)
    with SessionLocal() as db:
        db.add(RevokedToken(token=token.token))
        db.commit()
    return {"message": "Logged out"}


@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Access granted"}
```

## Production: Using Redis

For high-performance applications, use Redis:

```python
import redis
from authx import AuthX, AuthXConfig

auth = AuthX(config=AuthXConfig(JWT_SECRET_KEY="your-secret-key"))

redis_client = redis.Redis(host="localhost", port=6379, db=0)


@auth.set_callback_token_blocklist
def is_token_revoked(token: str) -> bool:
    return redis_client.exists(f"revoked:{token}") > 0


def revoke_token(token: str, expires_in: int = 86400):
    """Add token to blocklist with expiration."""
    redis_client.setex(f"revoked:{token}", expires_in, "1")
```

!!! tip "Token Expiration"
    Only store tokens in the blocklist until they would naturally expire. This keeps the blocklist small.

## Important Notes

!!! warning "Revoke Both Tokens"
    When logging out, revoke both access and refresh tokens:

    ```python
    @app.post("/logout")
    async def logout(request):
        access = await auth.get_access_token_from_request(request)
        refresh = await auth.get_refresh_token_from_request(request)

        BLOCKLIST.add(access.token)
        if refresh:
            BLOCKLIST.add(refresh.token)

        return {"message": "Logged out"}
    ```
