# Key Rotation

AuthX supports zero-downtime JWT signing key rotation. When you rotate keys, tokens signed with the previous key remain valid during a transition window while all new tokens are signed with the current key.

## How It Works

1. You deploy a new signing key via `JWT_SECRET_KEY` (or `JWT_PRIVATE_KEY`/`JWT_PUBLIC_KEY`)
2. You set the old key as `JWT_PREVIOUS_SECRET_KEY` (or `JWT_PREVIOUS_PUBLIC_KEY`)
3. AuthX **encodes** new tokens with the current key only
4. AuthX **decodes** tokens by trying the current key first, then falling back to the previous key
5. Once all old tokens have expired, you remove the previous key config

## Complete Example (Symmetric)

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from authx import AuthX, AuthXConfig, TokenPayload

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="new-secret-key-2026",
    JWT_PREVIOUS_SECRET_KEY="old-secret-key-2025",  # Still accepted during transition
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(data: LoginRequest):
    """New tokens are always signed with the current key."""
    if data.username == "test" and data.password == "test":
        token = auth.create_access_token(uid=data.username)
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")


@app.get("/protected")
def protected(payload: TokenPayload = Depends(auth.access_token_required)):
    """Accepts tokens signed with either the current or previous key."""
    return {"user": payload.sub}
```

## Testing the Flow

```bash
# Tokens signed with the OLD key still work
curl -H "Authorization: Bearer <old-token>" http://localhost:8000/protected
# {"user": "test"}

# Tokens signed with the NEW key also work
curl -H "Authorization: Bearer <new-token>" http://localhost:8000/protected
# {"user": "test"}

# Tokens signed with an UNKNOWN key are rejected
curl -H "Authorization: Bearer <unknown-token>" http://localhost:8000/protected
# 401 Unauthorized
```

---

## Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `JWT_PREVIOUS_SECRET_KEY` | `str` | `None` | Previous symmetric key for HS256/384/512 |
| `JWT_PREVIOUS_PUBLIC_KEY` | `str` | `None` | Previous public key for RS256/ES256/PS256 |

These only affect **decoding**. New tokens are always signed with `JWT_SECRET_KEY` / `JWT_PRIVATE_KEY`.

---

## Asymmetric Key Rotation (RS256)

For asymmetric algorithms, rotate the key pair and keep the previous **public** key:

```python
config = AuthXConfig(
    JWT_ALGORITHM="RS256",
    JWT_PRIVATE_KEY=NEW_PRIVATE_PEM,
    JWT_PUBLIC_KEY=NEW_PUBLIC_PEM,
    JWT_PREVIOUS_PUBLIC_KEY=OLD_PUBLIC_PEM,  # Decode-only fallback
)
```

!!! tip "Only the Public Key Is Needed"
    You only need to keep the previous **public** key. The old private key should be deleted once rotated.

---

## Rotation Procedure

### Step 1: Generate a New Key

```python
import secrets

new_key = secrets.token_urlsafe(32)
```

### Step 2: Deploy with Both Keys

```python
config = AuthXConfig(
    JWT_SECRET_KEY=new_key,
    JWT_PREVIOUS_SECRET_KEY=old_key,
)
```

### Step 3: Wait for Old Tokens to Expire

The transition window should be at least as long as your longest token expiry (typically `JWT_REFRESH_TOKEN_EXPIRES`).

### Step 4: Remove the Previous Key

```python
config = AuthXConfig(
    JWT_SECRET_KEY=new_key,
    # JWT_PREVIOUS_SECRET_KEY removed
)
```

---

## Environment Variables

Since `AuthXConfig` extends Pydantic `BaseSettings`, you can set keys via environment variables:

```bash
export JWT_SECRET_KEY="new-secret-key-2026"
export JWT_PREVIOUS_SECRET_KEY="old-secret-key-2025"
```

```python
config = AuthXConfig()  # Reads from environment automatically
```

---

## Best Practices

!!! warning "Never Reuse Old Keys"
    Once a key is retired from the previous slot, do not reuse it. Always generate fresh keys.

!!! tip "Automate Rotation"
    Consider rotating keys on a regular schedule (e.g., quarterly) and automating the deployment with environment variables or a secrets manager.

!!! note "Single Previous Key"
    AuthX supports one previous key at a time. If you need to rotate again before the first transition completes, ensure all tokens from the oldest key have expired first.

---

## Next Steps

- [Basic Usage](./basic-usage.md) - Getting started with AuthX
- [Refresh Tokens](./refresh.md) - Understanding token expiry and refresh flows
- [JWT Locations](./location.md) - Where tokens are read from
