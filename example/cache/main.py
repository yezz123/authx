import os
from datetime import datetime

import redis
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from authx import HTTPCache, cache, invalidate_cache

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
redis_client = redis.Redis.from_url(REDIS_URL)


class User:
    id: str = "112358"


user = User()
app = FastAPI(
    title="FastAPI Cache Example",
    description="This is a FastAPI cache example",
    version="0.1.0",
)

HTTPCache.init(redis_url=REDIS_URL, namespace="test_namespace")


@app.get("/b/home")
@cache(key="b.home", ttl_in_seconds=180)
async def home(request: Request, response: Response):
    return JSONResponse({"page": "home", "datetime": str(datetime.utcnow())})


@app.get("/b/logged-in")
@cache(key="b.logged_in.{}", obj="user", obj_attr="id")
async def logged_in(request: Request, response: Response, user=user):
    return JSONResponse(
        {"page": "home", "user": user.id, "datetime": str(datetime.utcnow())}
    )


@app.post("/b/logged-in")
@invalidate_cache(
    key="b.logged_in.{}", obj="user", obj_attr="id", namespace="test_namespace"
)
async def post_logged_in(request: Request, response: Response, user=user):
    return JSONResponse(
        {"page": "home", "user": user.id, "datetime": str(datetime.utcnow())}
    )
