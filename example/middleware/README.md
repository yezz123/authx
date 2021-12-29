# OAuth2 - Example Middleware

Starlette middleware for authentication through oauth2's via a secret key, which is often used to add authentication and authorization to a web application that interacts with an API on behalf of the user.

This middleware is intended to be used when the application relies on an external tenant (e.g. Microsoft AD) for authentication.

## How to run the example against Microsoft AD

Note: the values in capital such as `CLIENT_ID` are to be added to `example/middleware/.venv`.

1. Generate a secret (e.g. `openssl rand -base64 32`) and write its value on `SECRET_KEY`

2. Go to Azure AD, create an app registration (`app registrations`), give it a name, and add `http://localhost:5001/authorized` as a `Redirect URI`.
    * add the value on `Application (client) ID` to `CLIENT_ID`
    * add the value on `Endpoints > OpenID Connect metadata document` to `SERVER_METADATA_URL`

3. In `Certificates & secrets` tab, create a new client secret.
    * add the value of the key you just created under `Client secrets` to `CLIENT_SECRET`

## Run The Example

I Pre-built the docker configuration thats help to run the application locally and see all the middleware functionality.

```bash
# Run the server and build the image
$ make up
```

* When you visit `http://localhost:5001/public`, you will see that you are not authenticated.
* When you visit `http://localhost:5001/other`, you will be redirected to your tenant, to authenticate.
* Once authenticated, you will be redirected back to `http://localhost:5001/other`, and your email will appear.
