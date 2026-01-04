# User Serialization

AuthX can automatically retrieve user data from your database using the token's subject identifier.

## Complete Example

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)


# User model
class User(BaseModel):
    email: str
    firstname: str
    lastname: str


# Mock database
USERS_DB = {
    "john@example.com": {
        "email": "john@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "password": "secret123",
    }
}


# Define how to get user from token subject
@auth.set_subject_getter
def get_user_from_uid(uid: str) -> User:
    user_data = USERS_DB.get(uid)
    if user_data:
        return User(**{k: v for k, v in user_data.items() if k != "password"})
    return None


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/login")
def login(data: LoginRequest):
    user = USERS_DB.get(data.email)
    if user and user["password"] == data.password:
        token = auth.create_access_token(uid=data.email)
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")


@app.get("/me")
def get_me(user: User = Depends(auth.get_current_subject)):
    return {"user": user}
```

## How It Works

### 1. Define the Subject Getter

Create a function that retrieves user data from your database using the token's subject (`uid`):

```python
@auth.set_subject_getter
def get_user_from_uid(uid: str) -> User:
    user_data = USERS_DB.get(uid)
    if user_data:
        return User(**user_data)
    return None
```

### 2. Use in Routes

Use `auth.get_current_subject` as a dependency to get the user:

```python
@app.get("/me")
def get_me(user: User = Depends(auth.get_current_subject)):
    return {"email": user.email, "name": f"{user.firstname} {user.lastname}"}
```

Or use the shorthand property:

```python
@app.get("/me")
def get_me(user: User = auth.CURRENT_SUBJECT):
    return {"user": user}
```

## Testing

```bash
# Login
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"john@example.com", "password":"secret123"}' \
  http://localhost:8000/login
# {"access_token": "eyJ..."}

# Get current user
curl -H "Authorization: Bearer <token>" http://localhost:8000/me
# {"user": {"email": "john@example.com", "firstname": "John", "lastname": "Doe"}}
```

## With SQLAlchemy

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)

# Database setup
Base = declarative_base()
engine = create_engine("sqlite:///./users.db")
SessionLocal = sessionmaker(bind=engine)


class UserDB(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String)
    password = Column(String)
    firstname = Column(String)
    lastname = Column(String)


Base.metadata.create_all(bind=engine)


class User(BaseModel):
    id: str
    email: str
    firstname: str
    lastname: str

    class Config:
        from_attributes = True


@auth.set_subject_getter
def get_user_from_uid(uid: str) -> User | None:
    with SessionLocal() as db:
        user = db.query(UserDB).filter(UserDB.id == uid).first()
        if user:
            return User.model_validate(user)
    return None


@app.get("/me")
def get_me(user: User = Depends(auth.get_current_subject)):
    if user is None:
        raise HTTPException(404, detail="User not found")
    return {"user": user}
```

## Type Hints

AuthX is a generic class. You can specify the user type for better IDE support:

```python
# Option 1: Using model parameter
auth = AuthX(config=config, model=User)

# Option 2: Using generic syntax
auth: AuthX[User] = AuthX(config=config)
```
