# AuthenticationX 💫

![authx](https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png)

<p align="center">
    <em>Ready-to-use and customizable Authentications and Oauth2 management for FastAPI ⚡</em>
</p>

[![Test](https://github.com/yezz123/authx/actions/workflows/test.yml/badge.svg)](https://github.com/yezz123/authx/actions/workflows/test.yml)
[![Publish](https://github.com/yezz123/authx/actions/workflows/release.yml/badge.svg)](https://github.com/yezz123/authx/actions/workflows/release.yml)
[![Pypi](https://img.shields.io/pypi/pyversions/AuthX.svg?color=%2334D058)](https://pypi.org/project/AuthX)
[![codecov](https://codecov.io/gh/yezz123/AuthX/branch/main/graph/badge.svg?token=3j5znCNzDp)](https://codecov.io/gh/yezz123/AuthX)
[![PyPI](https://badge.fury.io/py/authx.svg)](https://badge.fury.io/py/authx)
[![Downloads](https://pepy.tech/badge/authx)](https://pepy.tech/project/authx)
[![framework](https://img.shields.io/badge/Framework-FastAPI-blue?style)](https://fastapi.tiangolo.com/)

<!--  -->

---

**Source Code**: <https://github.com/yezz123/authx>

**Get Started**: <https://authx.yezz.me/>

---

Add a Fully registration and authentication or authorization system to your
[FastAPI](https://fastapi.tiangolo.com/) project. **Authx** is designed to be as
customizable and adaptable as possible.

Authx is a fast, flexible and easy to use authentication and authorization
library for FastAPI. It is built on top of
[FastAPI](https://fastapi.tiangolo.com/) and
[starlette](https://www.starlette.io/).

## Features

- [x] Support Python 3.9+.
- [x] Extensible base user model.
- [x] Ready-to-use register, login, reset password and verify e-mail routes.
- [x] Ready-to-use Social login and Oauth2 routes.
    - [x] Full Configuration and customization.
    - [x] Ready-to-use social OAuth2 login flow.
- [x] Middleware Support for Oauth2 using `Authlib` and Starlette.
- [x] Dependency callable to inject current user in route.
- [x] Pluggable password validation
    - [x] Using Captcha Service.
    - [x] Implements the `HMAC` algorithm And `Hashlib` library.
- [x] Using Email Service. (SMTP)
- [x] Extensible Error Handling
- [x] High level API to manage users, roles and permissions
- [x] Using Redis as a session store & cache.
- [x] Support HTTPCache.
- [x] Customizable database backend:
    - [x] MongoDB async backend included thanks to
          [mongodb/motor](https://github.com/mongodb/motor)
    - [x] SQLAlchemy backend included thanks to
          [Encode/Databases](https://github.com/encode/databases)
- [x] Multiple customizable authentication backend:
    - [x] JWT authentication backend included
    - [x] Cookie authentication backend included
- [x] Full OpenAPI schema support, even with several authentication backend.
- [x] Provide a Docstring for each class and function.
- [x] Support Sessions and Pre-built CRUD functions and Instance to launch
      Redis.
- [x] Support SocketIO.
- [x] Support Middleware of [pyinstrument](https://pyinstrument.readthedocs.io/)
      to check your service performance.
- [x] Support Middleware for collecting and exposing [Prometheus](https://prometheus.io/) metrics.

## Project using

### Startup

```py
from fastapi import FastAPI
from authx import Authentication, User, RedisBackend

app = FastAPI()
# Set up Authentication & Authorization
auth = Authentication()

# Set up Pre-configured Routes
app.include_router(auth.auth_router, prefix="/api/users")
app.include_router(auth.social_router, prefix="/auth")
app.include_router(auth.password_router, prefix="/api/users")
app.include_router(auth.admin_router, prefix="/api/users")
app.include_router(auth.search_router, prefix="/api/users")

# Set Redis Cache
auth.set_cache(RedisBackend)
```

### Dependency injections

```py
# Set Anonymous User
@app.get("/anonym")
def anonym_test(user: User = Depends(auth.get_user)):
    pass


# Set Authenticated User
@app.get("/user")
def user_test(user: User = Depends(auth.get_authenticated_user)):
    pass


# Set Admin User (Only for Admins)
@app.get("/admin", dependencies=[Depends(auth.admin_required)])
def admin_test():
    pass
```

### Dependency injections only

```python
from authx import authx, RedisBackend

auth = authx()

auth.set_cache(RedisBackend)
```

## License

This project is licensed under the terms of the [MIT License](license.md).
