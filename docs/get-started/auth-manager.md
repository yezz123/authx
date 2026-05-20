# AuthManager and Policies

`AuthManager` lets one FastAPI app use multiple isolated `AuthX` instances. Each instance has its own `login_type`, JWT secret, token lifetime, token locations, and optional policy rules.

Use it when your application has fundamentally different identities such as admins, regular users, API clients, or service accounts.

## Multiple Login Types

```python
from fastapi import Depends, FastAPI
from authx import AuthManager, AuthX, AuthXConfig

app = FastAPI()

admin_auth = AuthX(
    config=AuthXConfig(
        JWT_SECRET_KEY="admin-secret-key",
        JWT_ACCESS_TOKEN_EXPIRES=3600,
        JWT_TOKEN_LOCATION=["headers"],
    ),
    login_type="admin",
)
user_auth = AuthX(
    config=AuthXConfig(
        JWT_SECRET_KEY="user-secret-key",
        JWT_ACCESS_TOKEN_EXPIRES=900,
        JWT_TOKEN_LOCATION=["headers", "cookies"],
    ),
    login_type="user",
)

manager = AuthManager()
manager.register(admin_auth)
manager.register(user_auth)
manager.handle_errors(app)


@app.post("/admin/login")
def admin_login(username: str):
    token = manager.create_access_token("admin", uid=username)
    return {"access_token": token, "login_type": "admin"}


@app.get("/admin/dashboard", dependencies=[Depends(manager.access_token_required("admin"))])
def admin_dashboard():
    return {"message": "Welcome Admin"}
```

Tokens created by a managed `AuthX` instance include a `login_type` claim automatically. A token from another registered login type is rejected with `LoginTypeMismatchError`.

## Policy Rules

Policies can combine scopes, subject attributes, resource attributes, environment data, and custom Python evaluators.

```python
from authx import PolicyCondition, PolicyRule

manager.add_policy_rule(
    PolicyRule(
        effect="allow",
        actions=["users:ban"],
        resources=["users"],
        scopes=["admin:*"],
        conditions=[
            PolicyCondition(source="environment", key="method", value="POST"),
        ],
    )
)


@app.post("/admin/users/{user_id}/ban")
def ban_user(payload=Depends(manager.policy_required("admin", "users:ban", "users"))):
    return {"banned_by": payload.sub}
```

Explicit deny rules win over allow rules. If no rule matches, access is denied by default.

## Custom Evaluators

```python
from authx import PolicyContext, PolicyRule


def active_account_only(context: PolicyContext, rule: PolicyRule) -> bool:
    return context.subject.get("account_status") == "active"


manager.add_policy_rule(
    PolicyRule(
        effect="allow",
        actions=["billing:read"],
        resources=["billing"],
        evaluators=[active_account_only],
    )
)
```

For single-type applications, the existing `AuthX` API remains unchanged. `AuthManager` is opt-in.
