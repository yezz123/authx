## Example

Lets see a little example of how to use the middleware, and Integrate it with
the application.

We could Create Our Project based on Starlette, instead of FastAPI.

### Create Crud Instance

Using `SQLAlchemy`, we can create a Crud instance, and we can use it to create a
Database and show multiple crud functionalities.

```py
import typing

from sqlalchemy import JSON, Column, MetaData, String, Table, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import create_session
from starlette.config import Config

config = Config(".env.sample")


class DB:
    def __init__(self) -> None:
        self._engine = create_engine(config("DATABASE_URL"))
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
```

- Here we are using the `create_engine` function to create a database engine,
  and we are using the `config` function to get the database url from the
  `.env.sample` file.
- We are using the `Table` function to create a table, and we are using the
  `Column` function to create the columns of the table.
- We are using the `create_session` function to create a session, and we are
  using the `Base` function to create the Base class.
- We are using the `prepare` function to prepare the Base class.

```py
    def put(self, user_id: str, token: typing.Dict[str, typing.Any]) -> None:
        self._session.merge(self._User(id=user_id, token=dict(token)))
        self._session.flush()
```

- Here we are using the `merge` function to merge the user, and we are using the
  `flush` function to flush the session.
- We are using the `id` and `token` attributes to create the user.
- We are using the `put` function to put the user in the database.

```py
    def get(self, user_id: str) -> typing.Optional[typing.Dict[str, typing.Any]]:
        result = (
            self._session.query(self._User).filter(self._User.id == user_id).first()
        )
        if result is not None:
            return result.token
```

- Here we are using the `query` function to query the database, and we are using
  the `filter` function to filter the query, and we are using the `first`
  function to get the first result of the query.
- We are using the `id` attribute to filter the query, and we are using the
  `token` attribute to get the token of the user.
- We are using the `get` function to get the token of the user.

```py
    def delete(self, user_id: str) -> None:
        self._session.query(self._User).filter(self._User.id == user_id).delete()
        self._session.flush()
```

- Here we are using the `query` function to query the database, and we are using
  the `filter` function to filter the query, and we are using the `delete`
  function to delete the user.
- We are using the `id` attribute to filter the query, and we are using the
  `flush` function to flush the session.
- We are using the `delete` function to delete the user.

### Create Middleware & App

Now After initializing the database, we can create the middleware and the app.

Let's Call our Imports and Initial the Environment Variables using the `Config`
function in `starlette.config`.

```py
from starlette.applications import Starlette
from starlette.config import Config
from starlette.datastructures import Secret
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from authx import MiddlewareOauth2

config = Config(".env.sample")
```

- Here we are using the `Config` function to get the environment variables from
  the `.env.sample` file.

```py
config.SECRET_KEY = config("SECRET_KEY", cast=Secret)
config.SERVER_METADATA_URL = config("SERVER_METADATA_URL", cast=str)
config.CLIENT_ID = config("CLIENT_ID", cast=str)
config.CLIENT_SECRET = config("CLIENT_SECRET", cast=Secret)
```

- Here we are using the `SECRET_KEY` and `SERVER_METADATA_URL` environment
  variables to set the `SECRET_KEY` and `SERVER_METADATA_URL` attributes of the
  `config` function.
- We are using the `CLIENT_ID` and `CLIENT_SECRET` environment variables to set
  the `CLIENT_ID` and `CLIENT_SECRET` attributes of the `config` function.

```py
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
```

- We Instance the application using the `Starlette` function, and we are using
  the `db` and `server_metadata_url` attributes of the `config` function to
  initialize the `db` and `server_metadata_url` attributes of the
  `AuthenticateMiddleware` class.
- We are using the `client_id` and `client_secret` attributes of the `config`
  function to initialize the `client_id` and `client_secret` attributes of the
  `AuthenticateMiddleware` class.
- We are using the `force_https_redirect` attribute of the `config` function to
  initialize the `force_https_redirect` attribute of the
  `AuthenticateMiddleware` class.
- We are using the `add_middleware` function to add the `SessionMiddleware`
  class to the application.

```py
@app.route("/other")
async def homepage(request):
    user = request.session.get("user")
    return JSONResponse(user)
```

- Here we are using the `route` function to create a route, and we are using the
  `get` function to get the user from the session.
- We are using the `JSONResponse` function to return the user as a JSON
  response.

```py
@app.route("/public")
async def homepage(request):
    user = request.session.get("user")
    payload = {"message": "User not authenticated"} if user is None else user
    return JSONResponse(payload)
```

- Here we are using the `route` function to create a route, and we are using the
  `get` function to get the user from the session.
- We are using the `payload` variable to create the payload of the response.
- We are using the `JSONResponse` function to return the payload as a JSON
  response.

To ensure that we can run the app we will use `uvicorn` and `httpx` to run the
app.

```py
if __name__ == "__main__":
    import logging
    import sys

    import uvicorn

    logger = logging.getLogger("httpx")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    uvicorn.run(app, host="localhost", port=5001)
```

- Here we are using the `if` statement to check if the `__name__` is equal to
  `__main__`.
- We import some libraries like `logging` and `sys`, and at the end we are using
  the `uvicorn` function to run the app.
- We are using the `getLogger` function to get the logger of the `httpx`
  library, and we are using the `setLevel` function to set the level of the
  logger to `DEBUG`.
- We are using the `addHandler` function to add the `StreamHandler` to the
  logger.
- We are using the `run` function to run the app.

#### Result

At the end of the process, we can run the app using the following command:

```sh
python -m app
```

We can see that the app is running on the following URL:

- When you visit `http://localhost:5001/public`, you will see that you are not
  authenticated.
- When you visit `http://localhost:5001/other`, you will be redirected to your
  tenant, to authenticate.
- Once authenticated, you will be redirected back to
  `http://localhost:5001/other`, and your email will appear.
