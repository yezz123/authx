import random
from datetime import timedelta
from typing import Any

from fastapi import Depends, FastAPI, Request, Response
from starlette.config import Config

from authx.cache import basicConfig
from authx.core import (
    SessionStorage,
    deleteSession,
    getSession,
    getSessionId,
    getSessionStorage,
    setSession,
)

app = FastAPI(
    title="Session example",
    description="This is an example of a session management with authx.",
)

config = Config("docker-compose.env")

basicConfig(
    redisURL=config("REDIS_URL"),
    sessionIdName=config("SESSION_ID_NAME"),
    sessionIdGenerator=lambda: str(random.randint(1000, 9999)),
    expireTime=timedelta(config("SESSION_EXPIRE_TIME")),
)


@app.post("/setSession")
async def _setSession(
    request: Request,
    response: Response,
    sessionStorage: SessionStorage = Depends(getSessionStorage),
):
    sessionData = await request.json()
    setSession(response, sessionData, sessionStorage)


@app.get("/getSession")
async def _setSession(session: Any = Depends(getSession)):
    return session


@app.post("/deleteSession")
async def _deleteSession(
    sessionId: str = Depends(getSessionId),
    sessionStorage: SessionStorage = Depends(getSessionStorage),
):
    deleteSession(sessionId, sessionStorage)
    return None
