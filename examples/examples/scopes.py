"""AuthX Scope Management Example.

This example demonstrates how to use scope-based authorization with AuthX:
- Creating tokens with scopes
- Protecting routes with required scopes
- Using wildcard scopes (e.g., "admin:*")
- AND/OR scope requirements

Scopes can be:
- Simple strings: "read", "write", "admin"
- Hierarchical: "users:read", "posts:write", "admin:settings"
- Wildcards: "admin:*" matches "admin:users", "admin:settings", etc.
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

from authx import AuthX, AuthXConfig, InsufficientScopeError
from authx.schema import TokenPayload

# Create FastAPI app
app = FastAPI(title="AuthX Scopes Example")

# Configure AuthX
auth_config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="your-secret-key",  # Use env var in production
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=auth_config)
auth.handle_errors(app)


# Custom exception handler for insufficient scopes
@app.exception_handler(InsufficientScopeError)
async def insufficient_scope_handler(request: Request, exc: InsufficientScopeError):
    """Handle insufficient scope errors with a 403 Forbidden response."""
    return HTTPException(
        status_code=403,
        detail={
            "error": "insufficient_scope",
            "message": str(exc),
            "required": exc.required,
            "provided": exc.provided,
        },
    )


# Models
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    scopes: list[str]


# Sample user database with roles/scopes
USERS = {
    "admin": {
        "password": "admin123",
        "scopes": ["admin:*"],  # Wildcard: access to all admin resources
    },
    "editor": {
        "password": "editor123",
        "scopes": ["posts:read", "posts:write", "posts:delete"],
    },
    "viewer": {
        "password": "viewer123",
        "scopes": ["posts:read", "users:read"],
    },
    "superuser": {
        "password": "super123",
        "scopes": ["admin:*", "posts:*", "users:*"],  # Multiple wildcards
    },
}


# Type alias for scope-protected dependencies
AdminRequired = Annotated[TokenPayload, Depends(auth.scopes_required("admin:*"))]
PostsReadRequired = Annotated[TokenPayload, Depends(auth.scopes_required("posts:read"))]
PostsWriteRequired = Annotated[TokenPayload, Depends(auth.scopes_required("posts:write"))]


@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    """Login and receive a token with user's scopes."""
    if data.username not in USERS:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = USERS[data.username]
    if user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token with user's scopes
    scopes = user["scopes"]
    access_token = auth.create_access_token(uid=data.username, scopes=scopes)

    return TokenResponse(access_token=access_token, scopes=scopes)


# ============================================================================
# SIMPLE SCOPE PROTECTION
# ============================================================================


@app.get("/posts")
async def list_posts(payload: PostsReadRequired):
    """List posts - requires 'posts:read' scope."""
    return {
        "message": "Posts retrieved successfully",
        "user": payload.sub,
        "user_scopes": payload.scopes,
    }


@app.post("/posts")
async def create_post(payload: PostsWriteRequired):
    """Create a post - requires 'posts:write' scope."""
    return {
        "message": "Post created successfully",
        "user": payload.sub,
    }


# ============================================================================
# WILDCARD SCOPE PROTECTION
# ============================================================================


@app.get("/admin/dashboard")
async def admin_dashboard(payload: AdminRequired):
    """Admin dashboard - requires 'admin:*' scope (any admin permission)."""
    return {
        "message": "Welcome to admin dashboard",
        "user": payload.sub,
        "user_scopes": payload.scopes,
    }


@app.get("/admin/users")
async def admin_users(payload: Annotated[TokenPayload, Depends(auth.scopes_required("admin:users"))]):
    """Admin users management - requires 'admin:users' scope.

    Note: A user with 'admin:*' will also have access due to wildcard matching.
    """
    return {
        "message": "Admin users page",
        "user": payload.sub,
    }


@app.get("/admin/settings")
async def admin_settings(payload: Annotated[TokenPayload, Depends(auth.scopes_required("admin:settings"))]):
    """Admin settings - requires 'admin:settings' scope.

    Note: A user with 'admin:*' will also have access due to wildcard matching.
    """
    return {
        "message": "Admin settings page",
        "user": payload.sub,
    }


# ============================================================================
# MULTIPLE SCOPES (AND logic - default)
# ============================================================================


@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    payload: Annotated[
        TokenPayload,
        Depends(auth.scopes_required("posts:read", "posts:delete")),  # AND: both required
    ],
):
    """Delete a post - requires BOTH 'posts:read' AND 'posts:delete' scopes."""
    return {
        "message": f"Post {post_id} deleted",
        "user": payload.sub,
    }


# ============================================================================
# MULTIPLE SCOPES (OR logic)
# ============================================================================


@app.get("/moderate")
async def moderate_content(
    payload: Annotated[
        TokenPayload,
        Depends(
            auth.scopes_required(
                "admin:*",
                "moderator",
                all_required=False,  # OR: any one scope is sufficient
            )
        ),
    ],
):
    """Moderate content - requires EITHER 'admin:*' OR 'moderator' scope."""
    return {
        "message": "Moderation access granted",
        "user": payload.sub,
        "user_scopes": payload.scopes,
    }


# ============================================================================
# MANUAL SCOPE CHECKING
# ============================================================================


@app.get("/profile")
async def get_profile(request: Request):
    """Profile with conditional features based on scopes."""
    token = await auth.get_access_token_from_request(request)
    payload = auth.verify_token(token, verify_csrf=False)

    profile = {
        "username": payload.sub,
        "scopes": payload.scopes,
    }

    # Manually check for additional features
    if payload.has_scopes("users:write"):
        profile["can_edit_profile"] = True
    else:
        profile["can_edit_profile"] = False

    if payload.has_scopes("admin:*"):
        profile["is_admin"] = True

    return profile


# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/")
def read_root():
    """Public endpoint with API documentation."""
    return {
        "message": "AuthX Scopes Example",
        "test_users": {
            "admin": {"password": "admin123", "scopes": ["admin:*"]},
            "editor": {"password": "editor123", "scopes": ["posts:read", "posts:write", "posts:delete"]},
            "viewer": {"password": "viewer123", "scopes": ["posts:read", "users:read"]},
            "superuser": {"password": "super123", "scopes": ["admin:*", "posts:*", "users:*"]},
        },
        "endpoints": {
            "POST /login": "Get token with scopes",
            "GET /posts": "Requires 'posts:read'",
            "POST /posts": "Requires 'posts:write'",
            "DELETE /posts/{id}": "Requires 'posts:read' AND 'posts:delete'",
            "GET /admin/dashboard": "Requires 'admin:*' (any admin scope)",
            "GET /admin/users": "Requires 'admin:users' (or 'admin:*')",
            "GET /admin/settings": "Requires 'admin:settings' (or 'admin:*')",
            "GET /moderate": "Requires 'admin:*' OR 'moderator'",
            "GET /profile": "Manual scope checking example",
        },
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on http://localhost:{port}")
    print("\nTest users:")
    for user, data in USERS.items():
        print(f"  {user}: {data['scopes']}")

    uvicorn.run(app, host="0.0.0.0", port=port)
