# Refreshing Tokens

JWTs come with a strict `exp` (Expiration Time), which means that a long session might lead to multiple logouts and `401 Authentication` errors. To mitigate such behavior, refresh tokens are employed to facilitate the generation of additional access tokens without requiring the user to log in again.

## Implicit refresh with Cookies

The most common way to refresh tokens is by using cookies. When the access token expires, the client sends a request to the server with the refresh token stored in a cookie. The server then generates a new access token and sends it back to the client in the response.

!!! warning
    Cookies are not supported in all environments, such as mobile applications, SDKs, or APIs. In such cases, you may need to implement an explicit refresh mechanism.

!!! note
    Work in progress: This feature needs to be documented.

## Explicit Refresh

In cases where implicit refresh isn't feasible—such as in mobile applications, SDKs, or APIs—you may need to explicitly declare the refresh logic in your application.

To implement an explicit refresh mechanism, you need to create a new route that accepts the refresh token and returns a new access token. This route should be protected by the `refresh_token_required` dependency, which will verify the refresh token and extract the payload.

!!! note
    The refresh token should be stored securely on the client side, and the route should be protected by HTTPS to prevent tampering.

```python
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Request
from authx import AuthX, TokenPayload

app = FastAPI()
security = AuthX()

class LoginForm(BaseModel):
    username: str
    password: str

class RefreshForm(BaseModel):
    refresh_token: str

@app.post('/login')
def login(data: LoginForm):
    if data.username == "test" and data.password == "test":
        access_token = security.create_access_token(data.username)
        refresh_token = security.create_refresh_token(data.username)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    raise HTTPException(401, "Bad username/password")


@app.post('/refresh')
async def refresh(request: Request, refresh_data: RefreshForm = None):
    """
    Refresh endpoint - creates a new access token using a refresh token

    Can accept the refresh token either:
    1. In the Authorization header
    2. In the request body as JSON
    """
    try:
        # First try to get the refresh token from the Authorization header
        try:
            refresh_payload = await security.refresh_token_required(request)
        except Exception as header_error:
            if not refresh_data or not refresh_data.refresh_token:
                # If we don't have a token in either place, raise the original error
                raise header_error

            # Manually decode and verify the refresh token
            token = refresh_data.refresh_token
            refresh_payload = security.verify_token(
                token,
                verify_type=True,
                type="refresh"
            )
        # Create a new access token
        access_token = security.create_access_token(refresh_payload.sub)
        return {"access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get('/protected', dependencies=[Depends(security.access_token_required)])
def protected():
    return "You have access to this protected resource"
```

In this example, the `/refresh` route accepts a refresh token either from the Authorization header or from the request body. Once verified, it generates a new access token to extend the session.

This example provides a flexible implementation of an explicit refresh mechanism. In a production scenario, you might want to retrieve the current access token to revoke it, thereby avoiding the generation of an infinite number of valid access tokens.

=== "1. Login"

    ```sh
    # To obtain tokens, we log in
    $ curl -s -X POST -H "Content-Type: application/json" -d '{"username":"test", "password":"test"}' http://0.0.0.0:8000/login
    {"access_token": "$TOKEN", "refresh_token": "$REFRESH_TOKEN"}
    ```
=== "2. Performing Sensitive Operations"

    ```sh
    # We request access to the protected route with the token
    $ curl -s -H "Authorization: Bearer $TOKEN" http://0.0.0.0:8000/protected
    "You have access to this protected resource"
    ```
=== "3. Refreshing Access Token (Using Header)"

    ```sh
    # To obtain a new access token using the Authorization header
    $ curl -s -X POST -H "Authorization: Bearer $REFRESH_TOKEN" -H "Content-Type: application/json" http://0.0.0.0:8000/refresh
    {"access_token": "$NEW_TOKEN"}
    ```
=== "4. Refreshing Access Token (Using JSON)"

    ```sh
    # To obtain a new access token using the request body
    $ curl -s -X POST -H "Content-Type: application/json" -d '{"refresh_token":"$REFRESH_TOKEN"}' http://0.0.0.0:8000/refresh
    {"access_token": "$NEW_TOKEN"}
    ```

As demonstrated in the final steps, the refreshing mechanism enables the acquisition of new tokens without the need for re-authentication, using either the Authorization header or the request body.
