# Basic Usage

The core concept of AuthX relies on generating access tokens and protecting routes. The following examples demonstrate how to use AuthX to quickly integrate these systems within your FastAPI application.

```py
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig

app = FastAPI(title="My Base App")

config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "SECRET_KEY"

security = AuthX(config=config)

@app.get('/login')
def login(username: str, password: str):
    if username == "test" and password == "test":
        token = security.create_access_token(uid=username)
        return {"access_token": token}
    raise HTTPException(401, detail={"message": "Bad credentials"})

@app.get("/protected", dependencies=[Depends(security.access_token_required)])
def get_protected():
    return {"message": "Hello World"}
```

## Getting Started

Let's build our first FastAPI application with AuthX.

As usual, you create your application with the `fastapi.FastAPI` object

```py hl_lines="1 4"
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig

app = FastAPI(title="My Base App")

config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "SECRET_KEY"

security = AuthX(config=config)
```

### Create the `AuthXConfig` Instance

```py hl_lines="2 6-7"
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig

app = FastAPI(title="My Base App")

config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "SECRET_KEY"

security = AuthX(config=config)
```

AuthX provides an `AuthXConfig` object (based on Pydantic's `BaseSettings`) to customize the behavior of JWT management.

Here, we enforce a **symmetric** encryption algorithm, specifically `"HS256"`, and set the `SECRET_KEY` as the key for encoding and decoding.

#### Handling Secrets with `AuthXConfig`

By design, JSON Web Tokens are not encrypted; you can try your own JWT on [https://jwt.io/](https://jwt.io/). However, your server will need secrets to sign tokens.

```py  hl_lines="8"
from fastapi import FastAPI
from authx import AuthX, AuthXConfig

app = FastAPI(title="My Base App")

config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "SECRET_KEY"

security = AuthX(config=config)
```

!!! warning "Secrets Location"
    As a best practice, do not use explicit secrets within your code. It is recommended to use environment variables to avoid any credential leakage.
    ```py
    import os
    from authx import AuthXConfig

    config = AuthXConfig()
    config.JWT_SECRET_KEY = os.getenv("SECRET_KEY")
    ```

!!! info "Note on Algorithm"
    For demonstration ease, we use a **symmetric** algorithm. Note that an **asymmetric** algorithm offers additional layers of protection.
    `"RS256"` is the recommended algorithm when signing JWTs.

### Create `AuthX` instance

You can now instantiate the `AuthX` object with your configuration

```py hl_lines="2 10"
from fastapi import FastAPI
from authx import AuthX, AuthXConfig

app = FastAPI(title="My Base App")

config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "SECRET_KEY"

security = AuthX(config=config)
```

!!! tip "Loading Configuration after `AuthX.__init__`"
    You can also load the configuration after the `AuthX` object is created. This is useful when you want to use the same `AuthX` object for multiple FastAPI applications.

    ```py
    config = AuthXConfig()
    config.JWT_SECRET_KEY = "SECRET_KEY"

    security = AuthX()
    security.load_config(config)
    ```

## Authentication

### Create the access token

To authenticate a user, create a `/login` route in the usual way with FastAPI.

```py hl_lines="4"
@app.get('/login')
def login(username: str, password: str):
    if username == "test" and password == "test":
        token = security.create_access_token(uid=username)
        return {"access_token": token}
    raise HTTPException(401, detail={"message": "Bad credentials"})
```

Once a user has provided valid credentials, use the `AuthX.create_access_token` method to generate a signed token. To associate the user with the token, utilize the `uid` argument.

!!! info "Note on Privacy"
    Avoid including personally identifiable information (PIDs) in the JWT since its content is fully readable. As a best practice, `uid` should typically be a user database index (not ordered). Consider using UUIDs for additional privacy.

!!! info "Note on Login Protection"
    The `/login` route above serves as a simple example. **Avoid passing credentials through query parameters** for security reasons. Implement thorough authentication logic to ensure a more robust login process.

=== "Request Access Token"

    ```sh
    $ curl -s -X GET "http://0.0.0.0:8000/login?username=test&password=test"
    {"access_token": "$TOKEN"}
    ```

### Protected Routes

Let's implement a simple `GET` route that can only be accessed by authenticated users.

```py
@app.get("/protected", dependencies=[Depends(security.access_token_required)])
def get_protected():
    return {"message": "Hello World"}
```

AuthX is compliant with FastAPI's [dependency injection system](https://fastapi.tiangolo.com/tutorial/dependencies/). It provides the `AuthX.access_token_required` method to enforce this behavior.

Whether a bad token or no token is provided, the server will prevent the execution of the route logic defined in `/protected`.

=== "curl without JsonWebToken"
    ```bash
    $ curl -s http://0.0.0.0:8000/protected
    {"detail":"Missing JWT in request"}
    ```

=== "With a bad JsonWebToken"
    ```bash
    $ curl -s -H "Authorization: Bearer dummytoken" http://0.0.0.0:8000/protected
    {"detail":"Unauthorized"}
    ```

=== "With a valid JsonWebToken"
    ```bash
    $ curl -s -H "Authorization: Bearer $TOKEN" http://0.0.0.0:8000/protected
    {"message": "Hello World"}
    ```

!!! failure "Default Exception Behavior"
    In the curl requests above, a `401` HTTP Error is raised when the token is not valid. By default, AuthX triggers a `500 Internal Server Error` HTTP Error. For the sake of simplicity, we won't delve into error handling in this section.
