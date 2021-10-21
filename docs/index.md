# AuthenticationX 💫

![authx](https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png)

<p align="center">
    <em>Ready to use and customizable Authentications and Oauth2 management for FastAPI ⚡</em>
</p>

[![codecov](https://codecov.io/gh/yezz123/AuthX/branch/main/graph/badge.svg?token=3j5znCNzDp)](https://codecov.io/gh/yezz123/AuthX)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b510202495654916843956856fd9a1f6)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=yezz123/AuthX&amp;utm_campaign=Badge_Grade)
[![PyPI version](https://badge.fury.io/py/AuthX.svg)](https://badge.fury.io/py/AuthX)
[![Downloads](https://pepy.tech/badge/authx/month)](https://pepy.tech/project/authx)
[![Downloads](https://pepy.tech/badge/authx/week)](https://pepy.tech/project/authx)
[![Lang](https://img.shields.io/badge/Language-Python-green?style)](https://www.python.org/)
[![framework](https://img.shields.io/badge/Framework-FastAPI-blue?style)](https://fastapi.tiangolo.com/)
[![Star Badge](https://img.shields.io/static/v1?label=%F0%9F%8C%9F&message=If%20Useful&style=style=flatcolor=BC4E99)](https://github.com/yezz123/AuthX)
[![Pypi](https://img.shields.io/pypi/pyversions/AuthX.svg?color=%2334D058)](https://pypi.org/project/AuthX)

---

**Source Code**: <https://github.com/yezz123/AuthX> (Closed-Source)

**Get Started**: <https://yezz123.github.io/AuthX/>

---

Add a Fully registration and authentication or authorization system to your [FastAPI](https://fastapi.tiangolo.com/) project. **AuthX** is designed to be as customizable and adaptable as possible.

__Note__: This is a **beta** version of AuthX.

## Features

- Extensible base user model.
- Ready-to-use register, login, reset password and verify e-mail routes.
- Ready to use Social login and Oauth2 routes. (now with Google, Facebook)
    - Soon with Microsoft, Twitter, Github, etc.
    - Ready-to-use social OAuth2 login flow
- Tested Project on [Docker](https://docker.com/).
- Dependency callable to inject current user in route
- Pluggable password validation
    - Using Captcha Service.
- Using Email Service. (SMTP)
- Extensible Error Handling
- High level API to manage users, roles and permissions
- Using Redis as a session store & cache.
- Customizable database backend:
    - MongoDB async backend included thanks to [mongodb/motor](https://github.com/mongodb/motor)
- Multiple customizable authentication backend:
    - JWT authentication backend included
    - Soon to be included Cookie authentication backend
- Full OpenAPI schema support, even with several authentication backend.
- Provide a Docstring for each class and function.

## Project using

```py hl_lines="1 3 5 6 10-14"
{!src/main.py!}
```

### Startup

```py hl_lines="17-18"
{!src/main.py!}
```

### Dependency injections

```py hl_lines="1 3 7 21-23 27-29 33-35"
{!src/main.py!}
```

### Dependency injections only

```python
from AuthX import AuthX

auth = AuthX(#Provide Config)

# startup
auth.set_cache(cache) # aioredis
```

## License

This project is licensed under the terms of the [MIT License](license.md).
