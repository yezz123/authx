# Token Callbacks

To address the issue of tokens without expiry dates or revoked tokens passing standard JWT validation, it's essential to verify if the provided token in the request has been revoked. Typically, this involves comparing the token against a blacklist of non-expired revoked tokens.

AuthX facilitates this revoked token check through a custom callback system.

## Example Usage

```py
from typing import Optional
from fastapi import FastAPI, Depends
from authx import AuthX, RequestToken

REVOKED_TOKEN = []


app = FastAPI()
security = AuthX()

@security.set_callback_token_blocklist
def is_token_revoked(token:str) -> bool:
    """Check if given token is revoked"""
    return token in REVOKED_TOKEN

# We define dependency here to avoid code repetition
get_token_dep = security.get_token_from_request(
    type="access",
    optional=False
)
get_optional_token_dep = security.get_token_from_request(
    type="access",
    optional=True
)

@app.get("/login")
def login():
    token = security.create_access_token(uid="john.doe@fastwt.com")
    return {"access_token": token}

@app.get("/token/optional")
def get_token(token: Optional[RequestToken] = Depends(get_optional_token_dep)):
    if token is not None
        return f"Your token is: {token} and is located in {token.location}"
    else:
        return "No token found"

@app.get("/token/mandatory", dependencies=[Depends(security.access_token_required)])
def get_token(token: RequestToken = Depends(get_token_dep)):
    return f"Your token is: {token} and is located in {token.location}"

@app.delete("/logout", dependencies=[Depends(security.access_token_required)])
def logout(token: RequestToken = Depends(get_token_dep)):
    REVOKED_TOKEN.append(token.token)
    return "OK"

@app.get("/profile", dependencies=[security.access_token_required])
def profile():
    return "You are authenticated"

```

### Define and assign the callback

First we need to create a function with a first `token` _str_ positional argument.
This function should return `True` is the token is considered **revoked**, `False` otherwise.

AuthX provides a `AuthX.set_callback_token_blocklist` decorator to assign a custom callback for revoked token validation.

Once a callback is assigned with `AuthX.set_callback_token_blocklist`, every time a valid token is required, the user defined callback is executed to check if the token is revoked.

We define the `is_token_revoked` callback as a function taking `token` as a main _str_ positional argument and returning a `bool`

**TYPE** `Callable[[str, ParamSpecKwargs], bool]` or `(str) -> bool`

```py  hl_lines="12-15"
from typing import Optional
from fastapi import FastAPI, Depends
from authx import AuthX, RequestToken

REVOKED_TOKEN = []


app = FastAPI()
security = AuthX()

@security.set_callback_token_blocklist # (1)!
def is_token_revoked(token:str) -> bool:
    """Check if given token is revoked"""
    return token in REVOKED_TOKEN
```

1. You can set callbacks with the `AuthX` decorator syntax, but the following method call would also work

    ```py
    def is_token_revoked(token:str) -> bool:
        """Check if given token is revoked"""
        return token in REVOKED_TOKEN

    security = AuthX()
    security.set_callback_token_blocklist(is_token_revoked)
    ```

!!! tip "Setting Callback syntax"
    You can set callbacks with the `AuthX` decorator syntax, but the following method call would also work
    ```py
    def is_token_revoked(token:str) -> bool:
        """Check if given token is revoked"""
        return token in REVOKED_TOKEN

    security = AuthX()
    security.set_callback_token_blocklist(is_token_revoked)
    ```

??? abstract "Feature Proposal - Decorator Naming"
    The verbosity of `AuthX.set_callback_token_blocklist` might encourage us to add shorter aliases in next releases

### Setting the dependencies

To avoid code repetition we define callbacks as follow. This step is not necessary but allows for cleaner code.
We use the `AuthX.get_token_from_request` to create a dependency that returns a `AuthX.RequestToken` instance.

`RequestToken` describe the JWT information contained in request. It acts as a `dataclass` containing a _str_ `token`, a `type` parameter to declare the type of token expected, a `location` to define where to token is located in request and a `csrf` double submit token if necessary.

```py
# We define dependency here to avoid code repetition
get_token_dep = security.get_token_from_request(
    type="access",
    optional=False
)
get_optional_token_dep = security.get_token_from_request(
    type="access",
    optional=True
)
```

We created 2 dependencies, `get_token_dep` & `get_optional_token_dep`, the main difference is based on the `optional` argument.

`get_optional_token_dep` return type is `Optional[RequestToken]`, meaning the execution will continue even if no token is available in request.

`get_token_dep` return type is `RequestToken`, meaning the dependency will enforce token availability in request, and raise a `MissingTokenError` otherwise.

!!! note
    The `AuthX.get_token_from_request` dependency **does not check** the token validity, it only returns the token
    if found in request. If no token appears in the request the dependency will return a `None` value.

    If you need to ensure a token is available use this dependency in conjunction with the `AuthX.token_required` dependency

```py hl_lines="1 2 8 9"
@app.get("/token/optional")
def get_token(token: Optional[RequestToken] = Depends(get_optional_token_dep)):
    if token is not None
        return f"Your token is: {token} and is located in {token.location}"
    else:
        return "No token found"

@app.get("/token/mandatory", dependencies=[Depends(security.access_token_required)])
def get_token(token: RequestToken = Depends(get_token_dep)):
    return f"Your token is: {token} and is located in {token.location}"
```

To showcase differences from the previously defined dependencies we coded 2 routes with a dummy principle, return the token and its location.

The `/token/mandatory` endpoint depends on both `get_token_dep` as a function dependency to retrieve the token and `AuthX.access_token_required` as a route dependency to enforce JWT validation.

The `/token/optional` endpoint does not require a token to be passed in request, and even if a token is passed it does not need to be a valid one.

### Revoke a token

In our example when the user request the `DELETE /logout` endpoint, we log out the user by adding the token in a blocklist. The same blocklist used to check for revoked tokens.

```py hl_lines="1 2"
@app.delete("/logout", dependencies=[Depends(security.access_token_required)])
def logout(token: RequestToken = Depends(get_token_dep)):
    REVOKED_TOKEN.append(token.token)
    return "OK"
```

!!! note "Revoking Access & Refresh"
    If during login you generated a couple of tokens as one `access` and one `refresh` token, ensure that both tokens are revoked.
    Since a user can use a `refresh` token to generate new `access` tokens, revoking only the `access` token is not enough to log out the user.

!!! note
    Again, even if we require `/logout` to have a token in request thanks to the `get_token_dep`, we also need to ensure this token is valid and therefore we also add the `AuthX.access_token_required` dependency.

=== "1. Get Profile"

    ```shell
    # No credential is provided
    $ curl -s http://0.0.0.0:8000/profile
     Internal Server Error # (1)!
    ```

    1. The `500 Internal Server Error` HTTP Error is the expected behavior because no error handling has been done

=== "2. Get Token"

    ```shell
    # Endpoint with optional=True
    $ curl -s http://0.0.0.0:8000/token/optional
    "No token found"
    # Endpoint with optional=False
    $ curl -s http://0.0.0.0:8000/token/mandatory
    Internal Server Error # (1)!
    ```

    1. The `500 Internal Server Error` HTTP Error is the expected behavior because no error handling has been done

=== "3. Login"

    ```shell
    # We generate a token to be conserved
    $ curl -s http://0.0.0.0:8000/login
    {"access_token": $TOKEN}
    # We generate a token to be revoked
    $ curl -s http://0.0.0.0:8000/login
    {"access_token": $REVOKED_TOKEN}
    ```
=== "4. Logout"

    ```shell
    # We call /logout with the token to be revoked
    $ curl -s --oauth2-bearer $REVOKED_TOKEN http://0.0.0.0:8000/logout
     "OK"
    ```
=== "5. Get Profile"

    ```shell
    # A genuine token is provided
    $ curl -s --oauth2-bearer $TOKEN http://0.0.0.0:8000/profile
    "You are authenticated"
    # A revoked token is provided
    $ curl -s --oauth2-bearer $REVOKED_TOKEN http://0.0.0.0:8000/profile
    Internal Server Error # (1)!
    ```

    1. The `500 Internal Server Error` HTTP Error is the expected behavior because no error handling has been done

=== "6. Get Token"

    ```shell
    # /token/optional returns a 200 for any tokens because no validation is required
    $ curl -s --oauth2-bearer $TOKEN http://0.0.0.0:8000/token/optional
    "Your token is: $TOKEN and is located in headers"
    $ curl -s --oauth2-bearer $REVOKED_TOKEN http://0.0.0.0:8000/token/optional
    "Your token is: $REVOKED_TOKEN and is located in headers"

    # /token/mandatory applies a validation step
    $ curl -s --oauth2-bearer $TOKEN http://0.0.0.0:8000/token/mandatory
    "Your token is: $TOKEN and is located in headers"
    $ curl -s --oauth2-bearer $REVOKED_TOKEN http://0.0.0.0:8000/token/mandatory
    Internal Server Error # (1)!
    ```

    1. The `500 Internal Server Error` HTTP Error is the expected behavior because no error handling has been done

## Using SQL ORM <small>(sqlalchemy)</small>

In a real world scenario, the token blocklist would be stored in a database. Here is an example using SQLAlchemy to store the revoked tokens.

```py
from typing import Optional
from fastapi import FastAPI, Depends
from authx import AuthX, RequestToken
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class RevokedToken(Base):
    __tablename__ = 'revoked_tokens'

    token = Column(String, primary_key=True)

engine = create_engine('sqlite:///./revoked_tokens.db')
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

REVOKED_TOKEN = []

app = FastAPI()
security = AuthX()

@security.set_callback_token_blocklist
def is_token_revoked(token: str) -> bool:
    """Check if given token is revoked"""
    with SessionLocal() as session:
        return session.query(RevokedToken).filter_by(token=token).first() is not None

# We define dependency here to avoid code repetition
get_token_dep = security.get_token_from_request(
    type="access",
    optional=False
)
get_optional_token_dep = security.get_token_from_request(
    type="access",
    optional=True
)

@app.get("/login")
def login():
    token = security.create_access_token(uid="john.doe@fastwt.com")
    return {"access_token": token}

@app.get("/token/optional")
def get_token(token: Optional[RequestToken] = Depends(get_optional_token_dep)):
    if token is not None:
        return f"Your token is: {token} and is located in {token.location}"
    else:
        return "No token found"

@app.get("/token/mandatory", dependencies=[Depends(security.access_token_required)])
def get_token(token: RequestToken = Depends(get_token_dep)):
    return f"Your token is: {token} and is located in {token.location}"

@app.delete("/logout", dependencies=[Depends(security.access_token_required)])
def logout(token: RequestToken = Depends(get_token_dep)):
    with SessionLocal() as session:
        revoked_token = RevokedToken(token=token.token)
        session.add(revoked_token)
        session.commit()
    return "OK"

@app.get("/profile", dependencies=[security.access_token_required])
def profile():
    return "You are authenticated"
```
