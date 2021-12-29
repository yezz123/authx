from db import DB
from starlette.applications import Starlette
from starlette.config import Config
from starlette.datastructures import Secret
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from authx import MiddlewareOauth2

config = Config(".env.sample")

config.SECRET_KEY = config("SECRET_KEY", cast=Secret)
config.SERVER_METADATA_URL = config("SERVER_METADATA_URL", cast=str)
config.CLIENT_ID = config("CLIENT_ID", cast=str)
config.CLIENT_SECRET = config("CLIENT_SECRET", cast=Secret)

app = Starlette()
db = DB()


class AuthenticateMiddleware(MiddlewareOauth2):
    PUBLIC_PATHS = {"/public"}


app.add_middleware(
    AuthenticateMiddleware,
    db=db,
    server_metadata_url=config.SERVER_METADATA_URL,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET,
    force_https_redirect=False,
)
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)


@app.route("/other")
async def homepage(request):
    user = request.session.get("user")
    return JSONResponse(user)


@app.route("/public")
async def homepage(request):
    user = request.session.get("user")
    payload = {"message": "User not authenticated"} if user is None else user
    return JSONResponse(payload)


if __name__ == "__main__":
    import logging
    import sys

    import uvicorn

    logger = logging.getLogger("httpx")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    uvicorn.run(app, host="localhost", port=5001)
