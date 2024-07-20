# User Serialization

JSON Web Tokens (JWT) primarily serve for authentication purposes. While they can carry data, it's advisable to avoid storing sensitive information in the JWT payload. Instead, JWTs commonly carry identifiers to retrieve necessary data about the user/recipient/subject.

AuthX simplifies user serialization and retrieval by providing a custom callback system. This system automates the retrieval of user data without the need for repetitive code or manual retrieval logic within each route.

Let's consider an example scenario where a user authenticates themselves with a JWT, and you want to retrieve related user data from a database.

## Authenticating Users

```python
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX
from pydantic import BaseModel

# Mockup user database
FAKE_DB = {
    "john@doe.com": {
        "email": "john@doe.com",
        "password": "testpassword",
        "firstname": "John",
        "lastname": "Doe"
    }
}

class User(BaseModel):
    email: str
    password: str
    firstname: str
    lastname: str

class LoginForm(BaseModel):
    email: str
    password: str

app = FastAPI()
security = AuthX(model=User)

@security.set_subject_getter
def get_user_from_uid(uid: str) -> User:
    return User.parse_obj(FAKE_DB.get(uid, {}))

@app.post('/login')
async def login(data: LoginForm):
    user = FAKE_DB.get(data.email)
    if not user or user["password"] != data.password:
        raise HTTPException(401, "Bad email/password")

    access_token = security.create_access_token(data.email)
    return {"access_token": access_token}

@app.get('/whoami')
async def whoami(user: User = Depends(security.get_current_subject)):
    return f"You are: {user.firstname} {user.lastname}"
```

### Serialization

#### Define User Model

First, create a Pydantic `User` model to represent user data. This model serves as an object mapper for user information.

```python
class User(BaseModel):
    email: str
    password: str
    firstname: str
    lastname: str
```

#### Configure AuthX

Explicitly provide the `model` parameter to `AuthX` for type hinting purposes. Also, set a custom callback to retrieve user data based on the provided identifier.

```python
security = AuthX(model=User) # (1)!

@security.set_subject_getter
def get_user_from_uid(uid: str) -> User:
    return User.parse_obj(FAKE_DB.get(uid, {}))
```

1. You can provide type hints with multiple syntax

    === "Hint by argument"
        ```py
        security = AuthX(model=User)
        ```
    === "Hint by Generic"
        ```py
        security = AuthX[User]()
        ```
    === "Hint by Typing"
        ```py
        security: AuthX[User] = AuthX()
        ```

!!! tip "Tip: Type Hint"
    The `AuthX` is a Python Generic object, you can use the `model` init parameter to enforce the type hinting.
    Even if you use user serialization, the `model` parameter is not mandatory, and is not used during execution except for your custom defined accessor

    === "Hint by argument"
        ```py
        security = AuthX(model=User)
        ```
    === "Hint by Generic"
        ```py
        security = AuthX[User]()
        ```
    === "Hint by Typing"
        ```py
        security: AuthX[User] = AuthX()
        ```

#### Retrieve User Context

With the custom callback set, use `AuthX.get_current_subject` to obtain the parsed user instance within routes.

```python
@app.get('/whoami')
async def whoami(user: User = Depends(security.get_current_subject)): # (1)!
    return f"You are: {user.firstname} {user.lastname}"
```

1. You can use `AuthX.CURRENT_SUBJECT` dependency alias (see [Aliases](../dependencies/aliases.md))

    ```py
    async def whoami(user: User = security.CURRENT_SUBJECT):
        ...
    ```

From the `whoami` function dependency you can access the `User` instance directly and use it without having to fetch the object inside the route logic.

??? abstract "Feature - Dependency Alias"
    `AuthX.get_current_subject` might not be explicit enough and is quiet long. AuthX provides aliases to avoid importing `fastapi.Depends`.
    You can use `AuthX.CURRENT_SUBJECT` dependency alias (see [Aliases](../dependencies/aliases.md))

    ```py
    @app.get('/whoami')
    async def whoami(user: User = security.CURRENT_SUBJECT):
        ...
    ```

=== "Login to get a token"

    ```shell
    $ curl -X POST -s \
        --json '{"email":"john@doe.com", "password":"testpassword"}'\
        http://0.0.0.0:8000/login
    {"access_token": $TOKEN}
    ```

=== "Request the user profile"

    ```shell
    $ curl -s --oauth2-bearer $TOKEN http://0.0.0.0:8000/whoami
    You are:
        Firstname: John
        Lastname: Doe
    ```

### Using SQL ORM <small>(sqlalchemy)</small>

If you're using an SQL ORM like SQLAlchemy, you can enhance user serialization with AuthX to fetch user data from your database. This is particularly useful for larger applications managing user information in a relational database.

!!! tip "Tip: SQLAlchemy"
    The following example uses SQLAlchemy to interact with a PostgreSQL database. You can replace the SQLAlchemy ORM with any other ORM of your choice.

```python
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String)
    password = Column(String)
    firstname = Column(String)
    lastname = Column(String)


class UserModel(BaseModel):
    email: str
    password: str
    firstname: str
    lastname: str


class UserORM:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def get(self, uid: str) -> UserModel:
        with self.Session() as session:
            user = session.query(User).filter(User.id == uid).first()
            return UserModel.parse_obj(user.__dict__) if user else UserModel()


app = FastAPI()

security = AuthX[UserModel]()

@security.set_subject_getter
def get_user_from_uid(uid: str) -> UserModel:
    return UserORM(engine).get(uid)
```
