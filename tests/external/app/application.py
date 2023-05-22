import typing

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import JSON, Column, MetaData, String, Table, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import create_session
from starlette.config import Config
from starlette.datastructures import Secret
from starlette.middleware.sessions import SessionMiddleware

from authx.external import MiddlewareOauth2


class DB:
    def __init__(self) -> None:
        self._engine = create_engine("sqlite:///users.db")
        _metatable = Table(
            "users",
            MetaData(bind=self._engine),
            *[
                Column("id", String, primary_key=True, nullable=False),
                Column("token", JSON),
            ],
        )
        _metatable.create(checkfirst=True)

        Base = automap_base(metadata=_metatable.metadata)
        Base.prepare()

        self._session = create_session(bind=self._engine)
        self._User = Base.classes.users

    def put(self, user_id: str, token: typing.Dict[str, typing.Any]) -> None:
        self._session.merge(self._User(id=user_id, token=dict(token)))
        self._session.flush()

    def get(self, user_id: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
        result = self._session.query(self._User).filter(self._User.id == user_id).first()
        if result is not None:
            return result.token

    def delete(self, user_id: str) -> None:
        self._session.query(self._User).filter(self._User.id == user_id).delete()
        self._session.flush()


config = Config(".env.sample")
config.SECRET_KEY = config("SECRET_KEY", cast=Secret)
config.SERVER_METADATA_URL = config("SERVER_METADATA_URL", cast=str)
config.CLIENT_ID = config("CLIENT_ID", cast=str)
config.CLIENT_SECRET = config("CLIENT_SECRET", cast=Secret)

app = FastAPI(
    title="FastAPI OAuth2 Example",
    description="A simple example of using OAuth2 with FastAPI",
    version="0.1.0",
    docs_url="/",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

db = DB()


class AuthenticateMiddleware(MiddlewareOauth2):
    # make the path `/public` public
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


@app.get("/other")
async def homepage(request):
    user = request.session.get("user")
    return JSONResponse(user)


@app.get("/public")
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
