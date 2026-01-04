# Scope Management

AuthX provides comprehensive scope-based authorization for fine-grained access control. Scopes allow you to define what resources or actions a user can access.

## Scope Formats

AuthX supports multiple scope formats:

| Format | Description | Example |
|--------|-------------|---------|
| Simple | Plain string identifiers | `"read"`, `"write"`, `"admin"` |
| Hierarchical | Colon-separated namespaces | `"users:read"`, `"posts:write"` |
| Wildcard | Match all under namespace | `"admin:*"` matches `"admin:users"`, `"admin:settings"` |

## Creating Tokens with Scopes

Use the `scopes` parameter when creating tokens:

```python
from authx import AuthX, AuthXConfig

config = AuthXConfig(JWT_SECRET_KEY="your-secret-key")
auth = AuthX(config=config)

# Create token with simple scopes
token = auth.create_access_token(
    uid="user123",
    scopes=["read", "write"]
)

# Create token with hierarchical scopes
token = auth.create_access_token(
    uid="user123",
    scopes=["users:read", "posts:write", "posts:delete"]
)

# Create token with wildcard scopes (grants all permissions in namespace)
admin_token = auth.create_access_token(
    uid="admin",
    scopes=["admin:*"]  # Access to admin:users, admin:settings, etc.
)
```

---

## Protecting Routes with Scopes

### Using `scopes_required()` Dependency

The primary way to protect routes is with the `scopes_required()` dependency:

```python
from fastapi import Depends, FastAPI
from authx import AuthX, AuthXConfig

app = FastAPI()
config = AuthXConfig(JWT_SECRET_KEY="your-secret-key")
auth = AuthX(config=config)

# Single scope required
@app.get("/users", dependencies=[Depends(auth.scopes_required("users:read"))])
async def list_users():
    return {"users": [...]}

# Multiple scopes required (AND - all must be present)
@app.delete(
    "/users/{id}",
    dependencies=[Depends(auth.scopes_required("users:read", "users:delete"))]
)
async def delete_user(id: int):
    return {"message": f"User {id} deleted"}
```

### Getting the Token Payload

If you need access to the token payload (to get user info or scopes):

```python
from typing import Annotated
from authx.schema import TokenPayload

@app.get("/profile")
async def get_profile(
    payload: Annotated[TokenPayload, Depends(auth.scopes_required("profile:read"))]
):
    return {
        "user": payload.sub,
        "scopes": payload.scopes,
    }
```

---

## AND vs OR Logic

By default, all specified scopes must be present (AND logic). Use `all_required=False` for OR logic:

### AND Logic (Default)

```python
# User must have BOTH scopes
@app.post(
    "/posts",
    dependencies=[Depends(auth.scopes_required("posts:read", "posts:write"))]
)
async def create_post():
    ...
```

### OR Logic

```python
# User needs at least ONE of these scopes
@app.get(
    "/moderate",
    dependencies=[Depends(
        auth.scopes_required("admin:*", "moderator", all_required=False)
    )]
)
async def moderate_content():
    ...
```

---

## Wildcard Scopes

Wildcards allow granting access to entire namespaces:

```python
# Token with wildcard scope
token = auth.create_access_token(
    uid="admin",
    scopes=["admin:*"]
)

# This route requires "admin:users"
@app.get("/admin/users", dependencies=[Depends(auth.scopes_required("admin:users"))])
async def admin_users():
    ...  # User with "admin:*" can access this!

# This route requires "admin:settings"
@app.get("/admin/settings", dependencies=[Depends(auth.scopes_required("admin:settings"))])
async def admin_settings():
    ...  # User with "admin:*" can access this too!
```

**Wildcard Matching Rules:**

- `"admin:*"` matches `"admin:users"`, `"admin:settings"`, `"admin:logs"`
- `"admin:*"` also matches `"admin"` (the namespace itself)
- `"admin:*"` matches `"admin:users:edit"` (nested scopes)
- `"users:*"` does NOT match `"admin:users"` (different namespace)

---

## Manual Scope Checking

For conditional logic based on scopes, use `TokenPayload.has_scopes()`:

```python
@app.get("/dashboard")
async def dashboard(request: Request):
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token, verify_csrf=False)

    response = {"user": payload.sub}

    # Check for specific scopes
    if payload.has_scopes("admin:*"):
        response["admin_panel"] = True

    if payload.has_scopes("reports:read", "reports:export"):
        response["export_enabled"] = True

    # OR logic
    if payload.has_scopes("editor", "admin", all_required=False):
        response["can_edit"] = True

    return response
```

---

## Handling Insufficient Scopes

When a user lacks required scopes, `InsufficientScopeError` is raised:

```python
from authx import InsufficientScopeError

@app.exception_handler(InsufficientScopeError)
async def scope_error_handler(request: Request, exc: InsufficientScopeError):
    return JSONResponse(
        status_code=403,
        content={
            "error": "insufficient_scope",
            "message": str(exc),
            "required": exc.required,
            "provided": exc.provided,
        }
    )
```

---

## Complete Example

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from authx import AuthX, AuthXConfig, InsufficientScopeError
from authx.schema import TokenPayload

app = FastAPI()
config = AuthXConfig(JWT_SECRET_KEY="secret")
auth = AuthX(config=config)

# User database with scopes
USERS = {
    "admin": {"password": "admin", "scopes": ["admin:*"]},
    "editor": {"password": "editor", "scopes": ["posts:read", "posts:write"]},
    "viewer": {"password": "viewer", "scopes": ["posts:read"]},
}


@app.post("/login")
def login(username: str, password: str):
    user = USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(401, "Invalid credentials")

    token = auth.create_access_token(uid=username, scopes=user["scopes"])
    return {"access_token": token, "scopes": user["scopes"]}


# Type aliases for common scope requirements
AdminRequired = Annotated[TokenPayload, Depends(auth.scopes_required("admin:*"))]
PostsRead = Annotated[TokenPayload, Depends(auth.scopes_required("posts:read"))]
PostsWrite = Annotated[TokenPayload, Depends(auth.scopes_required("posts:write"))]


@app.get("/posts")
async def list_posts(payload: PostsRead):
    return {"posts": [...], "user": payload.sub}


@app.post("/posts")
async def create_post(payload: PostsWrite):
    return {"message": "Post created", "user": payload.sub}


@app.get("/admin")
async def admin_panel(payload: AdminRequired):
    return {"message": "Admin access granted", "user": payload.sub}
```

---

## Best Practices

### 1. Use Hierarchical Scopes

Organize scopes by resource and action:

```python
scopes = [
    "users:read",
    "users:write",
    "users:delete",
    "posts:read",
    "posts:write",
    "admin:users",
    "admin:settings",
]
```

### 2. Use Wildcards for Admin Roles

```python
# Instead of listing every permission
scopes = ["admin:*"]  # Full admin access

# Or for resource-level admin
scopes = ["users:*"]  # Full access to user operations
```

### 3. Create Type Aliases

```python
from typing import Annotated

AdminOnly = Annotated[TokenPayload, Depends(auth.scopes_required("admin:*"))]
CanReadPosts = Annotated[TokenPayload, Depends(auth.scopes_required("posts:read"))]
CanWritePosts = Annotated[TokenPayload, Depends(auth.scopes_required("posts:write"))]
```

### 4. Keep Scopes Granular

Prefer `"posts:delete"` over just `"delete"` for clarity and flexibility.

### 5. Document Required Scopes

Use FastAPI's OpenAPI features to document scope requirements:

```python
@app.get(
    "/users",
    summary="List Users",
    description="Requires `users:read` scope",
    dependencies=[Depends(auth.scopes_required("users:read"))]
)
async def list_users():
    ...
```

---

## Full Working Example

For a complete working example, see:

- [scopes.py](https://github.com/yezz123/authx/blob/main/examples/examples/scopes.py)

Run the example:

```bash
cd examples/examples
python scopes.py
```

Then test with different users:

```bash
# Login as viewer (posts:read only)
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "viewer", "password": "viewer"}'

# Login as admin (admin:* - full access)
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```
