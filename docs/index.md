# AuthX

![authx](https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png)

[![Testing on Docker](https://github.com/yezz123/AuthX/actions/workflows/docker.yml/badge.svg)](https://github.com/yezz123/AuthX/actions/workflows/docker.yml)
[![Upload Python Package](https://github.com/yezz123/AuthX/actions/workflows/build.yml/badge.svg)](https://github.com/yezz123/AuthX/actions/workflows/build.yml)
[![MIT licensed](https://img.shields.io/github/license/yezz123/AuthX)](https://raw.githubusercontent.com/yezz123/AuthX/main/LICENSE)
[![PyPI version](https://badge.fury.io/py/AuthX.svg)](https://badge.fury.io/py/AuthX)
[![Downloads](https://pepy.tech/badge/authx/month)](https://pepy.tech/project/authx)

- Ready to use and customizable Authentications and Oauth2 management for FastAPI ⚡

---

**Source Code**: <https://github.com/yezz123/AuthX>

**Get Started**: `pip install AuthX`

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

## License

This project is licensed under the terms of the Apache-2.0 License.
