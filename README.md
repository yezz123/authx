# AuthX

![authx](https://user-images.githubusercontent.com/52716203/136656260-41e4dfd6-a20b-4cc9-bef8-66d8137607fe.png)

[![Downloads](https://pepy.tech/badge/authx/month)](https://pepy.tech/project/authx)
[![PyPI version](https://badge.fury.io/py/AuthX.svg)](https://badge.fury.io/py/AuthX)

- Ready to use and customizable Authentications and Oauth2 management for FastAPI ⚡

---

**Source Code**: <https://github.com/yezz123/AuthX>

**Project Board**: <https://trello.com/b/0NNZMP8T>

**Documentation**: Working on it...

---

Add a Fully registration and authentication or authorization system to your [FastAPI](https://fastapi.tiangolo.com/) project. **AuthX** is designed to be as customizable and adaptable as possible.

__Note__: This is a **beta** version of AuthX.

- This Project is inspired from [fastapi-users](https://github.com/fastapi-users/fastapi-users) - Ready-to-use and customizable users management for FastAPI.

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

## Project using

```python
# auth.py
...
from AuthX import Authentication

auth = Authentication()

# main.py
...
from .auth import auth
...
app.include_router(auth.auth_router, prefix="/api/users")
app.include_router(auth.social_router, prefix="/auth")
app.include_router(auth.password_router, prefix="/api/users")
app.include_router(auth.admin_router, prefix="/api/users")
app.include_router(auth.search_router, prefix="/api/users")
...
```

### Startup

```python
# in a startup event
from .auth import auth
...
auth.set_cache(cache) # aioredis client
auth.set_database(database) # motor client
...
```

### Dependency injections

```python
from fastapi import APIRouter, Depends
from AuthX import User
from .auth import auth

router = APIRouter()

@router.get("/anonim")
def anonim_test(user: User = Depends(auth.get_user)):
  ...

@router.get("/user")
def user_test(user: User = Depends(auth.get_authenticated_user)):
  ...

@router.get("/admin", dependencies=[Depends(auth.admin_required)])
def admin_test():
  ...

```

### Dependency injections only

```python
from AuthX import AuthX
auth = AuthX(...)

# startup
...
auth.set_cache(cache) # aioredis
...
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
