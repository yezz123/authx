# AuthenticationX 💫

![authx](https://user-images.githubusercontent.com/52716203/136962014-280d82b0-0640-4ee5-9a11-b451b338f6d8.png)

<p align="center">
    <em>Ready to use and customizable Authentications and Oauth2 management for FastAPI ⚡</em>
</p>

[![Testing on Docker](https://github.com/yezz123/AuthX/actions/workflows/docker.yml/badge.svg)](https://github.com/yezz123/AuthX/actions/workflows/docker.yml)
[![Upload Python Package](https://github.com/yezz123/AuthX/actions/workflows/build.yml/badge.svg)](https://github.com/yezz123/AuthX/actions/workflows/build.yml)
[![MIT licensed](https://img.shields.io/github/license/yezz123/AuthX)](https://raw.githubusercontent.com/yezz123/AuthX/main/LICENSE)
[![PyPI version](https://badge.fury.io/py/AuthX.svg)](https://badge.fury.io/py/AuthX)
[![Downloads](https://pepy.tech/badge/authx/month)](https://pepy.tech/project/authx)
[![Downloads](https://pepy.tech/badge/authx/week)](https://pepy.tech/project/authx)
[![Lang](https://img.shields.io/badge/Language-Python-green?style)](https://github.com/yezz123)
[![framework](https://img.shields.io/badge/Framework-FastAPI-blue?style)](https://fastapi.tiangolo.com/)
[![Star Badge](https://img.shields.io/static/v1?label=%F0%9F%8C%9F&message=If%20Useful&style=style=flatcolor=BC4E99)](https://github.com/yezz123/AuthX)
[![Pypi](https://img.shields.io/pypi/pyversions/AuthX.svg?color=%2334D058)](https://pypi.org/project/AuthX)

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

## Project using

```python
from fastapi import FastAPI
from AuthX import Authentication

app = FastAPI()
auth = Authentication()

app.include_router(auth.auth_router, prefix="/api/users")
app.include_router(auth.social_router, prefix="/auth")
app.include_router(auth.password_router, prefix="/api/users")
app.include_router(auth.admin_router, prefix="/api/users")
app.include_router(auth.search_router, prefix="/api/users")
...
```

### Startup

```python
from fastapi import FastAPI
from AuthX import Authentication

app = FastAPI()
auth = Authentication()

app.include_router(auth.auth_router, prefix="/api/users")
app.include_router(auth.social_router, prefix="/auth")
app.include_router(auth.password_router, prefix="/api/users")
app.include_router(auth.admin_router, prefix="/api/users")
app.include_router(auth.search_router, prefix="/api/users")

# Set MongoDB and Redis Cache
auth.set_cache(cache) # aioredis client
auth.set_database(database) # motor client
```

### Dependency injections

```python
from fastapi import FastAPI,APIRouter, Depends
from AuthX import User
from AuthX import Authentication

app = FastAPI()
auth = Authentication()
router = APIRouter()


app.include_router(auth.auth_router, prefix="/api/users")
app.include_router(auth.social_router, prefix="/auth")
app.include_router(auth.password_router, prefix="/api/users")
app.include_router(auth.admin_router, prefix="/api/users")
app.include_router(auth.search_router, prefix="/api/users")

# Set MongoDB and Redis Cache
auth.set_cache(cache) # aioredis client
auth.set_database(database) # motor client

# Set Anonymous User
@router.get("/anonym")
def anonym_test(user: User = Depends(auth.get_user)):
    pass

# Set Authenticated User
@router.get("/user")
def user_test(user: User = Depends(auth.get_authenticated_user)):
    pass

#
@router.get("/admin", dependencies=[Depends(auth.admin_required)])
def admin_test():
    pass

```

### Dependency injections only

```python
from AuthX import AuthX

auth = AuthX(#Provide Config)

# startup
auth.set_cache(cache) # aioredis
```

## Development

### Setup environment

You should create a virtual environment and activate it:

```bash
python -m venv venv/
```

```bash
source venv/bin/activate
```

And then install the development dependencies:

```bash
pip install -r requirements.dev.txt
```

### Run tests

You can run all the tests with:

```bash
make test
```

The command will start a MongoDB container for the related unit tests. So you should have [Docker](https://www.docker.com/get-started) installed.

Alternatively, you can run `pytest` yourself. The MongoDB unit tests will be skipped if no server is available on your local machine:

```bash
pytest
```

### Format the code

Execute the following command to apply `pre-commit` formatting:

```bash
make lint
```

## Contributing

As you see the Package still under development, you can contribute to it, also its a closed source project.

- Then how i can contribute? 🤔
  - You could contact the Maintainer of this project on :
    - [Email](mailto:yasserth19@gmail.com)
    - [Twitter](https://twitter.com/THyasser1)
    - [telegram](https://t.me/yezz123)
- Where i can see the Project Roadmap? 🤔
  - I use to manage AuthX on [Trello](https://trello.com/b/0NNZMP8T), you could check and see all the tasks if you could help me to do it.

## License

This project is licensed under the terms of the Apache-2.0 License.
