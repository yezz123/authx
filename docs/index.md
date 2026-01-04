
<p align="center">
<a href="https://authx.yezz.me" target="_blank">
    <img src="https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png" alt="authx">
</a>
<p align="center">
    <em>Ready-to-use and customizable Authentications and Oauth2 management for FastAPI ⚡</em>
</p>
</p>

---

|Project |Status |
| --- | --- |
| CI | [![ CI ]( https://github.com/yezz123/authx/actions/workflows/ci.yml/badge.svg )]( https://github.com/yezz123/authx/actions/workflows/ci.yml )  [![ pre-commit.ci status ]( https://results.pre-commit.ci/badge/github/yezz123/authx/main.svg )]( https://results.pre-commit.ci/latest/github/yezz123/authx/main )  [![ Codecov ]( https://codecov.io/gh/yezz123/authx/branch/main/graph/badge.svg )]( https://codecov.io/gh/yezz123/authx ) |
| Meta | [![ Package version ]( https://img.shields.io/pypi/v/authx?color=%2334D058&label=pypi%20package )]( https://pypi.org/project/authx )  [![ Downloads ]( https://static.pepy.tech/badge/authx )]( https://pepy.tech/project/authx )  [![ Pydantic Version 2 ]( https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json )]( https://pydantic.dev )  [![ Ruff ]( https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json )]( https://github.com/astral-sh/ruff ) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=yezz123_authx&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=yezz123_authx) |

---

**Source Code**: <https://github.com/yezz123/authx>

**Documentation**: <https://authx.yezz.me/>

---

Add a fully featured authentication and authorization system to your [FastAPI](https://fastapi.tiangolo.com/) project. **AuthX** is designed to be simple, customizable, and secure.

## Installation

=== "pip"

    <div class="termy">

    ```console
    $ pip install authx
    ```

    </div>

=== "uv"

    <div class="termy">

    ```console
    $ uv add authx
    ```

    </div>

## Quick Start

Here's a complete working example you can copy and run:

```python
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig

app = FastAPI()

# Configure AuthX
config = AuthXConfig(
    JWT_SECRET_KEY="your-secret-key",  # Change this in production!
    JWT_TOKEN_LOCATION=["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)  # Register error handlers for proper responses

@app.post("/login")
def login(username: str, password: str):
    if username == "test" and password == "test":
        token = auth.create_access_token(uid=username)
        return {"access_token": token}
    raise HTTPException(401, detail="Invalid credentials")

@app.get("/protected", dependencies=[Depends(auth.access_token_required)])
def protected():
    return {"message": "Hello World"}
```

**Test it:**

```bash
# Login to get a token
curl -X POST "http://localhost:8000/login?username=test&password=test"
# {"access_token": "eyJ..."}

# Access protected route
curl -H "Authorization: Bearer <your-token>" http://localhost:8000/protected
# {"message": "Hello World"}
```

## Features

- Support for Python 3.9+ and Pydantic 2
- JWT authentication with multiple token locations:
  - Headers (Bearer token)
  - Cookies (with CSRF protection)
  - Query parameters
  - JSON body
- Access and refresh token support
- Token freshness for sensitive operations
- Token blocklist/revocation
- Extensible error handling

### Extra Features

Install [`authx-extra`](https://github.com/yezz123/authx-extra) for additional features:

- Redis session store and cache
- HTTP caching
- Performance profiling with pyinstrument
- Prometheus metrics

**Note:** Check [Release Notes](https://authx.yezz.me/release/) for the latest updates.
