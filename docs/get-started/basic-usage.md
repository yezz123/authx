# Basic Usage

The core concept of Authx relies on generating access tokens and protecting routes. The following examples demonstrate how to use Authx to quickly integrate those systems within your FastAPI application.

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

Let's build our first FastAPI application with Authx.

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
