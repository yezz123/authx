# AuthenticationX 💫

![authx](https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png)

<p align="center">
    <em>Ready-to-use and customizable Authentications and Oauth2 management for FastAPI ⚡</em>
</p>

[![Test](https://github.com/yezz123/authx/actions/workflows/build.yml/badge.svg)](https://github.com/yezz123/authx/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/yezz123/AuthX/branch/main/graph/badge.svg?token=3j5znCNzDp)](https://codecov.io/gh/yezz123/AuthX)
[![PyPI version](https://badge.fury.io/py/authx.svg)](https://badge.fury.io/py/authx)
[![Downloads](https://pepy.tech/badge/authx)](https://pepy.tech/project/authx)
[![Lang](https://img.shields.io/badge/Language-Python-green?style)](https://www.python.org/)
[![framework](https://img.shields.io/badge/Framework-FastAPI-blue?style)](https://fastapi.tiangolo.com/)
[![Pypi](https://img.shields.io/pypi/pyversions/AuthX.svg?color=%2334D058)](https://pypi.org/project/AuthX)

<a href="https://www.producthunt.com/posts/authx?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-authx" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=318189&theme=light" alt="AuthX - A FastAPI package for Auth made by a human not an AI | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>
<a href="https://www.buymeacoffee.com/tahiri" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

---

**Source Code**: <https://github.com/yezz123/AuthX>

**Get Started**: <https://authx.yezz.codes/>

---

Add a Fully registration and authentication or authorization system to your [FastAPI](https://fastapi.tiangolo.com/) project. **AuthX** is designed to be as customizable and adaptable as possible.

__Note__: This is a **beta** version of AuthX.

## Features

- Support Python 3.8+.
- Fully OpenAPI schema support.
- Extensible base user model.
- Ready-to-use register, login, reset password and verify e-mail routes.
- Ready-to-use Social login and Oauth2 routes. (now with Google, Facebook)
    - Soon with Microsoft, Twitter, Github, etc.
    - Ready-to-use social OAuth2 login flow
- Dependency callable to inject current user into route
- Pluggable password validation
    - Using Captcha Service.
- Using Email Service. (SMTP)
- Extensible Error Handling
- High level API to manage users, roles and permissions
- Using Redis as a session store & cache.
- Customizable database backend:
    - MongoDB async backend included thanks to [mongodb/motor](https://github.com/mongodb/motor)
- Multiple authentication strategies:
    - JWT authentication backend included
    - Cookie based authentication (coming soon)
- Provide a Docstring for each class and function.

## Project using

```py hl_lines="1 3 6 7 11-15"
{!src/main.py!}
```

### Startup

```py hl_lines="4 18-19"
{!src/main.py!}
```

### Dependency injections

```py hl_lines="1 3 7 22-24 28-30 34-36"
{!src/main.py!}
```

### Dependency injections only

```python
from authx import authx
from authx.database import RedisBackend

auth = authx()

# startup
auth.set_cache(RedisBackend) # aioredis
```

## License

This project is licensed under the terms of the [MIT License](license.md).
