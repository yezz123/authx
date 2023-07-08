# OAuth2 Middleware

!!! warning
     You need to install dependencies for the middleware you want to use

A middleware for FastAPI that enables authentication and authorization using JSON Web Tokens (JWT).

The purpose of this middleware is to incorporate authentication and authorization functionalities into an API, such as FastAPI, by utilizing access tokens obtained from an external authentication provider like `Microsoft AD` or `Auth0`.

It is primarily designed for scenarios where an API relies on an external identity provider for authentication and authorization, and where clients are capable of requesting their own access tokens.

In this setup, the API is not required to directly communicate with the identity provider;

its sole responsibility is to verify that the access tokens are properly signed by the identity provider.

## How to install

This middleware relies exclusively on the `python-jose` library, which it utilizes for decoding and validating JWTs.

<div class="termy">

```console
$ pip install authx[oauth2]

---> 100%
```

</div>
## How to Use

To enable authentication and authorization in your FastAPI application using the `MiddlewareOauth2` from the `authx.external` module, follow these steps:

1. Import the necessary modules and classes:

```python
from fastapi import FastAPI
from authx.external import MiddlewareOauth2
```

2. Create a FastAPI application instance:

```python
app = FastAPI()
```

3. Add the `MiddlewareOauth2` middleware to your application, specifying the configuration parameters:

```python
app.add_middleware(MiddlewareOauth2,
    providers={
        'google': {
            'keys': 'https://www.googleapis.com/oauth2/v3/certs',
            'issuer': 'https://accounts.google.com',
            'audience': '852159111111-xxxxxx.apps.googleusercontent.com',
        }
    },
    public_paths={'/'},
)
```

4. Configure the middleware by providing the necessary parameters:
   - `providers`: A dictionary that contains the authentication provider details. In this example, we use Google as the provider, but you can configure other providers as needed.
     - `keys`: The URL that provides the public keys used to verify the JWT signatures. For Google, this is `'https://www.googleapis.com/oauth2/v3/certs'`.
     - `issuer`: The URL of the identity provider. For Google, this is `'https://accounts.google.com'`.
     - `audience`: The audience value that identifies your application. This should be obtained from the identity provider. In this example, it is `'852159111111-xxxxxx.apps.googleusercontent.com'`.
   - `public_paths`: A set of public paths that do not require authentication. In this example, only the root path `'/'` is considered a public path.

### Token Validation

Once the middleware is configured, every route except the root path (`/`) requires an `authorization` header with the format `Bearer {token}`. The token must meet the following conditions:

- It should be a valid JWT.
- It should be issued by the specified `issuer` to the specified `audience`.
- It should be signed by one of the keys obtained from the `keys` URL.
- It should not have expired.

If any of these conditions are not met, the middleware will respond with a `401` status code. If the `authorization` header is missing or has an invalid format, a `400` response will be returned.

When a valid request is received, the middleware extracts all the claims from the JWT and adds them to the `oauth2-claims` field in the request's scope. You can access these claims using the following code snippet:

```python
...
def home(request):
    ...
    claims = request.scope['oauth2-claims']
    ...
```

If your identity provider includes custom claims in the JWT, you can use them for further authorization logic.

## Websockets

When establishing a websocket connection, the same JWT-based authentication method is required as for regular HTTP requests. If the token is invalid (as defined below), the connection will be terminated with code 1008.

## CORS

To enable pre-flight checks, you need to add the [CORS middleware](https://www.starlette.io/middleware/#cors-preflight-requests) after adding the authentication middleware. This ensures that the CORS middleware takes precedence and handles the preflight check. Additionally, the `authorization` header must be allowed in CORS, so that the browser includes it in the actual request.

```python
from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(AuthenticateMiddleware, ...)

app.add_middleware(CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=['authorization'],
)
```

## Details

The `providers` argument should be a dictionary where the keys can be arbitrary, and the values should be dictionaries containing three keys:

- `issuer`
- `audience`
- `keys`

### Issuer (iss)

The issuer is used by the middleware, in conjunction with python-Jose, to validate that the token was issued by a specific entity. Examples of issuers include:

- Microsoft: `https://login.microsoftonline.com/<ad_tenant_id>/v2.0`
- Google: `https://accounts.google.com`

You can find this value in the `iss` key of the `https://.../.well-known/openid-configuration` URL.

### Audience (aud)

Similar to the issuer, the audience is used by the middleware to verify that the token was intended for this API. Examples of audiences from different providers include:

- Microsoft: `https://<app-name>.azurewebsites.net`
- Google: `<tenant>-<project>.apps.googleusercontent.com`

The audience value can be obtained when configuring the application in the identity provider specific to your use case.

### Keys (jwks)

The `keys` represent the public keys of the identity provider. These keys have corresponding private keys used to sign the token. The middleware relies on Python-Jose to verify that the token was signed by one of the keys in this field.

The `keys` can be provided as a URL or an object. If a URL is used, the middleware will fetch the keys from that URL. Examples of URLs include:

- Microsoft: `https://login.microsoftonline.com/<tenant-id>/discovery/v2.0/keys`
- Google: `https://www.googleapis.com/oauth2/v3/certs`

The URL for fetching keys can be found in the `jwks_uri` key of the `https://.../.well-known/openid-configuration` URL.

Alternatively, instead of a URL, you can provide a JWK (JSON Web Key) set or another non-standard variation that is accepted by python-jose. The JWK set should be in the following format:

```json
{'keys': [
    {
        "kid": "...",
        "e": "AQAB",
        "kty": "RSA",
        "alg": "RS256",
        "n": "...",
        "use": "sig"
    },
]}
```

There is a tradeoff between providing a JWK set or a URL. When providing a JWK set, the middleware does not need access to the public internet to validate tokens, making it suitable for deployment in environments without internet access. However, keep in mind that JWK sets are subject to rotation by the identity provider, requiring you to redeploy the application with the updated public keys.

#### Decoding

The signature of the token is verified using the provided keys.

 If the token carries an `at_hash` key in its payload, it will be ignored. This is because decoding the access token is required to validate it, but the middleware does not have access to the access token itself.

### Key Caching Management

Some providers have rotating keys that the server needs to keep up-to-date. To refresh keys periodically, you can pass the `key_refresh_minutes` parameter to the middleware. By default, key refresh is disabled, meaning the key remains constant and is the same as the initially fetched key from the provider.
