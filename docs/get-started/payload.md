# Accessing Payload Data

When working with routes, it's often necessary to access data from a payload. This guide will show you how to accomplish this using Authx.

Authx introduces the `TokenPayload` class, a Pydantic `BaseModel` designed to handle JWT claims and operations. When Authx generates a token, it can be serialized into an easy-to-use `TokenPayload` instance.

## Storing Additional Data

By default, the `authx.create_[access|refresh]_token` methods handle standard JWT claims such as issue date, expiry time, and issuer identity. However, you can store additional data by passing keyword arguments to these methods.

For instance:

```python
token = security.create_access_token(uid="USER_UNIQUE_IDENTIFIER", foo="bar")
```

Keep in mind that the additional data passed as keyword arguments must be JSON serializable. Failure to adhere to this requirement will result in a `TypeError`. For example:

```python
from datetime import datetime
security.create_access_token(uid="USER_UNIQUE_IDENTIFIER", foo=datetime(2023, 1, 1, 12, 0))
```

## Accessing Data in Routes

JWT authentication allows you to scope an endpoint's logic to a specific user or recipient without explicitly referencing them. This is particularly useful for endpoints like `/me` or `/profile`.

To access data within your routes, you can use the `authx.access_token_required` dependency. When used as a parameter dependency, it returns a `TokenPayload` instance from a valid JWT. This payload can then be used to retrieve user data within your route logic.

However, using `authx.access_token_required` as a function dependency may lead to code repetition and the inclusion of fetching code outside your route logic.

Here's an example of how to use `authx.access_token_required` in a FastAPI application:

```python
from fastapi import FastAPI, Depends
from authx import AuthX, TokenPayload, AuthXConfig

app = FastAPI()
config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
security = AuthX(config=config)

@app.get('/token')
def get_token():
    token = security.create_access_token(uid="USER_ID", foo="bar", age=22)
    return {"access_token": token}

@app.get('/profile')
def get_profile(payload: TokenPayload = Depends(security.access_token_required)):
    return {
        "id": payload.sub,
        "age": getattr(payload, "age"),
        "foo": getattr(payload, "foo"),
    }
```

In this example, the `get_token` endpoint generates a token, while the `get_profile` endpoint utilizes `authx.access_token_required` to retrieve and utilize the token payload within its logic.

Whether used as a function argument or a route/decorator argument, `authx.access_token_required` enforces the validity of the token, throwing an exception if the token is invalid.

With access to the `payload` object, you can incorporate additional fields included with `authx.create_[access|refresh]_token` into your route logic.
