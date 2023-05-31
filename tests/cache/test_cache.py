import os
from datetime import datetime

import redis
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from authx.external import HTTPCache, cache, invalidate_cache

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/2")
redis_client = redis.from_url(REDIS_URL)


class User:
    id: str = "112358"


user = User()
app = FastAPI()

HTTPCache.init(redis_url=REDIS_URL, namespace="test_namespace")


@app.get("/b/home")
@cache(key="b.home", ttl_in_seconds=180)
async def home(request: Request, response: Response):
    return JSONResponse({"page": "home", "datetime": str(datetime.utcnow())})


@app.get("/b/logged-in")
@cache(key="b.logged_in.{}", obj="user", obj_attr="id")
async def logged_in(request: Request, response: Response, user=user):
    return JSONResponse({"page": "home", "user": user.id, "datetime": str(datetime.utcnow())})


async def my_ttl_callable():
    return 3600


@app.get("/b/ttl_callable")
@cache(key="b.ttl_callable_expiry", ttl_func=my_ttl_callable)
async def path_with_ttl_callable(request: Request, response: Response):
    return JSONResponse({"page": "path_with_ttl_callable", "datetime": str(datetime.utcnow())})


@app.post("/b/logged-in")
@invalidate_cache(key="b.logged_in.{}", obj="user", obj_attr="id", namespace="test_namespace")
async def post_logged_in(request: Request, response: Response, user=user):
    return JSONResponse({"page": "home", "user": user.id, "datetime": str(datetime.utcnow())})


@app.get("/b/profile")
@cache(key="b.profile.{}", obj="user", obj_attr="id")
async def logged_in(request: Request, response: Response, user=user):
    return JSONResponse({"page": "profile", "user": user.id, "datetime": str(datetime.utcnow())})


@app.post("/b/invalidate_multiple")
@invalidate_cache(
    keys=["b.logged_in.{}", "b.profile.{}"],
    obj="user",
    obj_attr="id",
    namespace="test_namespace",
)
async def invalidate_multiple(request: Request, response: Response, user=user):
    return JSONResponse({"page": "invalidate_multiple", "datetime": str(datetime.utcnow())})


def test_invalidate_multiple():
    client = TestClient(app)
    redis_client.flushdb()
    response = client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.status_code == 200
    response = client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    response2 = client.get(
        "/b/profile",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response2.status_code == 200
    response2 = client.get(
        "/b/profile",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response2.headers["Cache-hit"] == "true"
    response3 = client.post(
        "/b/invalidate_multiple",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response3.status_code == 200
    assert redis_client.get("test_namespace:b.logged_in.112358") is None
    assert redis_client.get("test_namespace:b.profile.112358") is None


def test_home_cached_response():
    client = TestClient(app)
    redis_client.flushdb()
    response = client.get(
        "/b/home",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.status_code == 200
    response = client.get(
        "/b/home",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers["Cache-hit"] == "true"


def test_with_ttl_callable():
    import pytest

    client = TestClient(app)
    redis_client.flushdb()
    response = client.get(
        "/b/ttl_callable",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.status_code == 200
    response = client.get(
        "/b/ttl_callable",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers["Cache-hit"] == "true"
    assert pytest.approx(redis_client.ttl("test_namespace:b.ttl_callable_expiry"), rel=1e-3) == 3600


def test_home_cached_with_current_user():
    client = TestClient(app)
    redis_client.flushdb()

    response = client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.status_code == 200

    response = client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers["Cache-hit"] == "true"
    assert response.status_code == 200
    value = redis_client.get("test_namespace:b.logged_in.112358")
    assert value is not None


def test_cache_invalidation():
    client = TestClient(app)
    redis_client.flushdb()

    response = client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.status_code == 200

    response = client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers["Cache-hit"] == "true"
    assert response.status_code == 200
    value = redis_client.get("test_namespace:b.logged_in.112358")
    assert value is not None

    client.post(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )

    response = client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers.get("Cache-hit", None) is None
