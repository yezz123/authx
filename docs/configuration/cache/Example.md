# Full Example

Here is an example of a full configuration to use HTTPCache Functionality.

```python
import os
import redis
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from authx import HTTPCache, cache, invalidate_cache

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/3")
redis_client = redis.Redis.from_url(REDIS_URL)

class User:
    id: str = "112358"

user = User()
app = FastAPI()

HTTPCache.init(redis_url=REDIS_URL, namespace='test_namespace')

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

```
