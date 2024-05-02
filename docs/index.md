---
hide:
  - navigation
---

<p align="center">
<a href="https://authx.yezz.me" target="_blank">
    <img src="https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png" alt="AuthX">
</a>
<p align="center">
    <em>Ready-to-use and customizable Authentications and Oauth2 management for FastAPI ⚡</em>
</p>
<p align="center">
<a href="https://github.com/yezz123/authx/actions/workflows/ci.yml" target="_blank">
    <img src="https://github.com/yezz123/authx/actions/workflows/ci.yml/badge.svg" alt="lint">
</a>
<a href="https://results.pre-commit.ci/latest/github/yezz123/authx/main" target="_blank">
    <img src="https://results.pre-commit.ci/badge/github/yezz123/authx/main.svg" alt="pre-commit.ci status">
</a>
<a href="https://pypi.org/project/authx" target="_blank">
    <img src="https://img.shields.io/pypi/v/authx?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://codecov.io/gh/yezz123/authx">
    <img src="https://codecov.io/gh/yezz123/authx/branch/main/graph/badge.svg"/>
</a>
<a href="https://pepy.tech/project/authx" target="_blank">
    <img src="https://static.pepy.tech/badge/authx" alt="Total Downloads">
</a>
<a href="https://pydantic.dev" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json" alt="Pydantic Version 2">
</a>
<a href="https://github.com/astral-sh/ruff" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
</a>
</p>
</p>

---

**Source Code**: <https://github.com/yezz123/authx>

**Documentation**: <https://authx.yezz.me/>

---

Add a Fully registration and authentication or authorization system to your
[FastAPI](https://fastapi.tiangolo.com/) project. **AuthX** is designed to be as
customizable and adaptable as possible.

## Installation

<div class="termy">

```console
$ pip install authx

---> 100%
```

</div>

## Features

- Support Python 3.8+ & Pydantic 2.0+.
- Multiple customizable authentication backend:
  - JWT authentication backend included
    - JWT encoding/decoding for application authentication
    - Automatic detection of JWTs in requests:
      - JWTs in headers
      - JWTs in cookies
      - JWTs in query parameters
      - JWTs in request bodies
  - Cookie authentication backend included
- Middleware for authentication and authorization through JWT.
- Extensible Error Handling System.

### Extra Features

!!! notes

    AuthX is designed to be as customizable and adaptable as possible.

    So you need to install [`authx-extra`](https://github.com/yezz123/authx-extra) to get extra features.

- Using Redis as a session store & cache.
- Support HTTPCache.
- Support Sessions and Pre-built CRUD functions and Instance to launch Redis.
- Support Middleware of [pyinstrument](https://pyinstrument.readthedocs.io/) to check your service performance.
- Support Middleware for collecting and exposing [Prometheus](https://prometheus.io/) metrics.

**Note:** Check [Release Notes](https://authx.yezz.me/release/).

## Project using

Here is a simple way to kickstart your project with AuthX:

```python
from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig, RequestToken

app = FastAPI()

config = AuthXConfig(
     JWT_ALGORITHM = "HS256",
     JWT_SECRET_KEY = "SECRET_KEY",
     JWT_TOKEN_LOCATION = ["headers"],
)

auth = AuthX(config=config)
auth.handle_errors(app)

@app.get('/login')
def login(username: str, password: str):
     if username == "xyz" and password == "xyz":
          token = auth.create_access_token(uid=username)
          return {"access_token": token}
     raise HTTPException(401, detail={"message": "Invalid credentials"})

@app.get("/protected", dependencies=[Depends(auth.get_token_from_request)])
def get_protected(token: RequestToken = Depends()):
     try:
          auth.verify_token(token=token)
          return {"message": "Hello world !"}
     except Exception as e:
          raise HTTPException(401, detail={"message": str(e)}) from e
```
