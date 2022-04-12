# Session

This a supported Redis Based Session Storage for you FastAPI Application, you can use it with any Session Backend.

Before doing that check that you install the pre-built requirements.

We use `redis-py` a Python client for Redis that is built on top of the Redis server.

## Features

--------

- [x] Dependency injection to protect routes
- [x] Compatible with FastAPI's auto generated docs
- [x] Pydantic models for verifying session data
- [x] Abstract session backend so you can build one that fits your needs
- [x] Abstract frontends to choose how you extract the session ids (cookies, header, etc.)
- [x] Create verifiers based on the session data.
- [x] Compatible with any Redis Configuration.

### Redis Configuration

Before setting up our Sessions Storage and our CRUD Backend, we need to configure our Redis Instance.

`BasicConfig` is a function help us setting up the Instance Information like Redis Link Connection or ID Name or Expiration Time.

#### Default Config

- [x] url of Redis: `redis://localhost:6379/0`
- [x] name of sessionId: `ssid`
- [x] generator function of `sessionId`: `lambda :uuid.uuid4().hex`
- [x] expire time of session in redis: `6 hours`

```py
import random
from datetime import timedelta
from authx.cache import basicConfig

basicConfig(
    redisURL="redis://localhost:6379/1",
    sessionIdName="sessionId",
    sessionIdGenerator=lambda: str(random.randint(1000, 9999)),
    expireTime=timedelta(days=1),
)
```

### Sessions Functions

When it come to way of storing our sessions, we need to create a function that will be used to store our sessions.

Authx give the developer the choice of using between a pre setting Crud Functionalities like `getSession` or `deleteSession`..

Also a `SessionStorage` Class where we initial the connections and the functions to store and get or delete our sessions.

```py
from typing import Any

from fastapi import Depends, FastAPI, Request, Response

from authx.core import (
    SessionStorage,
    deleteSession,
    getSession,
    getSessionId,
    getSessionStorage,
    setSession,
)

app = FastAPI(title=__name__)


@app.post("/setSession")
async def _setSession(
    request: Request, response: Response, sessionStorage: SessionStorage = Depends(getSessionStorage)
):
    sessionData = await request.json()
    setSession(response, sessionData, sessionStorage)


@app.get("/getSession")
async def _setSession(session: Any = Depends(getSession)):
    return session


@app.post("/deleteSession")
async def _deleteSession(
    sessionId: str = Depends(getSessionId), sessionStorage: SessionStorage = Depends(getSessionStorage)
):
    deleteSession(sessionId, sessionStorage)
    return None
```
