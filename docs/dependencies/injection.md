# Dependency Injection

AuthX integrates with FastAPI's dependency injection system. You can apply authentication at different levels.

## Route-Level Protection

Protect individual routes:

```python
from fastapi import FastAPI, Depends
from authx import AuthX, AuthXConfig, TokenPayload

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


# Option 1: Just protect the route (no payload access)
@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Access granted"}


# Option 2: Protect and get payload
@app.get("/me")
def get_me(payload: TokenPayload = Depends(auth.access_token_required)):
    return {"user_id": payload.sub}
```

## Application-Level Protection

Protect all routes in the app:

```python
from fastapi import FastAPI, Depends
from authx import AuthX, AuthXConfig, TokenPayload

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)

# All routes require authentication
app = FastAPI(dependencies=[Depends(auth.access_token_required)])
auth.handle_errors(app)


@app.get("/")
def home():
    return {"message": "Authenticated"}


@app.get("/me")
def get_me(payload: TokenPayload = Depends(auth.access_token_required)):
    return {"user_id": payload.sub}
```

## Router-Level Protection

Protect a group of routes using `APIRouter`:

```python
# main.py
from fastapi import FastAPI
from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


@app.get("/")
def home():
    return {"message": "Public"}


@app.get("/login")
def login():
    return {"access_token": auth.create_access_token(uid="user")}
```

```python
# admin_router.py
from fastapi import APIRouter, Depends
from main import auth

# All routes in this router require authentication
router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(auth.access_token_required)]
)


@router.get("/dashboard")
def dashboard():
    return {"message": "Admin Dashboard"}


@router.get("/users")
def list_users():
    return {"users": ["user1", "user2"]}
```

```python
# main.py (continued)
from admin_router import router

app.include_router(router)
```

## Complete Example

```python
from fastapi import FastAPI, APIRouter, Depends, HTTPException
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


# Public routes
@app.get("/")
def home():
    return {"message": "Welcome"}


@app.post("/login")
def login(data: LoginRequest):
    if data.username == "admin" and data.password == "admin":
        return {"access_token": auth.create_access_token(uid=data.username)}
    raise HTTPException(401, detail="Invalid credentials")


# Protected router
protected_router = APIRouter(
    prefix="/api",
    dependencies=[Depends(auth.access_token_required)]
)


@protected_router.get("/me")
def get_me(payload: TokenPayload = Depends(auth.access_token_required)):
    return {"user_id": payload.sub}


@protected_router.get("/data")
def get_data():
    return {"data": [1, 2, 3]}


app.include_router(protected_router)
```

## Testing

```bash
# Public route - works without token
curl http://localhost:8000/
# {"message": "Welcome"}

# Login
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin", "password":"admin"}' \
  http://localhost:8000/login
# {"access_token": "eyJ..."}

# Protected route - requires token
curl http://localhost:8000/api/data
# {"message": "Missing JWT in request", "error_type": "MissingTokenError"}

curl -H "Authorization: Bearer <token>" http://localhost:8000/api/data
# {"data": [1, 2, 3]}
```
