# Json Web Token

At this part of the configuration, you can configure the Json Web Token authentication, which is used to authenticate the user, and to generate the token, also stored in the cache.

using [`pyjwt`](https://pyjwt.readthedocs.io/en/stable/) a Python library which allows you to encode and decode JSON Web Tokens (JWT).

## Encode & Decode JWT

We Gonna create a Function used to Create access tokens, and a Function used to decode access tokens, also create a refresh token used
as a logout mechanism.

```py
# jwt.py
from AuthX.core.jwt import JWTBackend

cache_backend = # Redis Configuration
access_expiration = # Access Token Expiration
refresh_expiration = # Refresh Token Expiration
jwt_backend = JWTBackend(
    cache_backend, private_key, public_key,
    access_expiration, refresh_expiration)
```

Here we just create a JWTBackend object, which is used to create and decode tokens using:

* `cache_backend`: the cache backend used to store the tokens.
* `private_key`: the private key used to sign the tokens.
* `public_key`: the public key used to verify the tokens.
* `access_expiration`: the expiration time of the access token.
* `refresh_expiration`: the expiration time of the refresh token.

Now, lets create the Function used to create access tokens.

```py
async def create_token():
    token = jwt_backend._create_token({}, "access")
    payload = await jwt_backend.decode_token(token)
```

__Notes:__ : For testing this function, you can Mock the `cache_backend` & assert the payload, to understand you can check the Tests [core/jwt.py](https://github.com/yezz123/AuthX/blob/main/tests/core/test_core_jwt.py).

Now, lets create the Function used to decode access tokens.

```py
def test_decode_token():
    payload = await jwt_backend.decode_token(token)
```

We assign the `token`: where we created the access token, to the `payload` variable.

## Access Token

The Access Token is used to authenticate the user, and to generate the token, also stored in the cache.
Now after understanding the concept of Creating a token & Decode one lets do the Rest of the configuration, which is used to create the Access Token to let the user authenticate.

```py
def test_create_access_token():
    access_token = jwt_backend.create_access_token({})
    payload = await jwt_backend.decode_token(access_token)
```

Here, we have:

* `payload`: the payload of the access token.
* `_access_expiration`: the expiration time of the access token. (int)

## Refresh Token

Refresh Token is used as a logout mechanism, and is used to generate a new access token.

```py
def test_create_refresh_token():
    refresh_token = jwt_backend.create_refresh_token({})
    payload = await jwt_backend.decode_token(refresh_token)
```

Same as the Access Token, we have:

* `payload`: the payload of the refresh token.
* `_refresh_expiration`: the expiration time of the refresh token. (int)

__Notes__: For testing this and create a TestCases always assert a `payload.get` & check the refresh token expiration time.

## Revoke Token

The Revoke Token is used to revoke the access token, and is used to generate a new access token, this one is based more on the cache backend.

```py
def logout():
    from datetime import datetime
    from AuthX.core.jwt import JWTBackend

    key = # Key to revoke
    epoch = datetime.utcfromtimestamp(0)
    ts = int((datetime.utcnow() - epoch).total_seconds()) + 10
    await jwt_backend._cache.set(key, ts, 10)
    payload = await jwt_backend.decode_token(jwt_backend.create_access_token({"id": 1})
    await jwt_backend._cache.delete(key)
```

Here we have:

* `key`: the key to revoke.
* `epoch`: the epoch time.
* `ts`: the timestamp.
* `payload`: the payload of the access token.

!!! info
    We need to create a new access token, because the refresh token is used to generate a new access token.
