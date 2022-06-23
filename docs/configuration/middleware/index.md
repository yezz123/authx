# Middleware

## Oauth2

The OAuth 2.0 authorization framework is a protocol that allows a user to grant
a third-party web site or application access to the user's protected resources,
without necessarily revealing their long-term credentials or even their
identity.

Starlette middleware for authentication through oauth2's via a secret key, which
is often used to add authentication and authorization to a web application that
interacts with an API on behalf of the user.

Thats why AuthX provide a Configuration `MiddlewareOauth2` to configure the
OAuth2 middleware.

```py
from authx import MiddlewareOauth2
```

Lets take a look at the example:

```py
class AuthenticateMiddleware(MiddlewareOauth2):
    PUBLIC_PATHS = {"/public"}
```

Here we are using the `MiddlewareOauth2` class to configure the OAuth2
middleware, and we are using the `PUBLIC_PATHS` attribute to define the paths
that are not protected by the middleware, or we can say that the paths that are
not protected by the middleware are public.

So for example if we run the application on `http://localhost:5001/public`, we
will see that we are not authenticated.

And This feature is very useful when we want to protect some of the paths of the
application, but we want to allow the public to access those paths.

This Feature can be used in both a FastAPI application and a Starlette
application, cause mostly its depend on starlette, but we can use it in a
FastAPI application as well.

➡️ [Example](example.md)
