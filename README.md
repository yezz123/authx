# AuthX

- Ready to use and customizable Authentications and Oauth2 management for FastAPI ⚡

## Getting Started

### Prerequisites

- Python 3.9
- FastAPI
- Docker

### Project setup

```sh
# clone the repo
$ git clone https://github.com/yezz123/AuthX.git

# move to the project folder
$ cd DogeAPI
```

### Creating virtual environment

- Create a virtual environment using virtualenv.

```shell
# creating virtual environment
$ virtualenv venv

# activate virtual environment
$ source venv/bin/activate

# install all dependencies
$ pip install -r requirements.txt
```

## Running the Docker Container

- We have the Dockerfile created in above section. Now, we will use the Dockerfile to create the image of the FastAPI app and then start the FastAPI app container.
- Using a preconfigured `Makefile` tor run the Docker Compose:

```sh
# Pull the latest image
$ make pull

# Build the image
$ make build

# test the image
$ make test

```

##

Project using :

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
