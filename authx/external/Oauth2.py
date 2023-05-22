import logging

from authlib.integrations import starlette_client
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class MiddlewareOauth2:
    """
    Middleware for authentication through Oauth2.
    which is often used to add authentication and authorization to a web application that interacts with an API on behalf of the user.
    """

    REDIRECT_PATH = "/authorized"

    # list of paths that are public and do not require authentication
    PUBLIC_PATHS = set()

    def __init__(
        self,
        app: ASGIApp,
        server_metadata_url: str,
        client_id: str,
        client_secret: str,
        db=None,
        force_https_redirect=True,
    ) -> None:
        self.app = app
        self.db = db
        self._force_https_redirect = force_https_redirect

        self._client = starlette_client.StarletteRemoteApp(
            starlette_client.StartletteIntegration("starlette"),
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=server_metadata_url,
            client_kwargs={"scope": "openid email profile"},
        )

    def _redirect_uri(self, request: Request):
        """
        The URI of the redirect path. This should be registered on whatever provider is declared.
        """
        port = request.url.port
        port = "" if port is None else f":{str(port)}"
        scheme = request.url.scheme
        if scheme == "http" and self._force_https_redirect:
            scheme = "https"
        return f"{scheme}://{request.url.hostname}{port}{self.REDIRECT_PATH}"

    async def _authenticate(self, scope: Scope, receive: Receive, send: Send):
        """
        Authenticate the user, and redirect to the original path.
        """
        request = Request(scope)

        logger.info(f'Authenticating a user arriving at "{request.url.path}"')

        if request.url.path != self.REDIRECT_PATH:
            # store the original path of the request to redirect to when the user authenticates
            request.session["original_path"] = str(request.url)

            # any un-authenticated request is redirected to the tenant
            redirect_uri = self._redirect_uri(request)
            response = await self._client.authorize_redirect(request, redirect_uri)
        else:
            logger.info("Fetching id token...")
            # try to construct a user from the access token
            try:
                token = await self._client.authorize_access_token(request)
                user = await self._client.parse_id_token(request, token)
                assert user is not None
            except Exception:
                # impossible to build a user => invalidate the whole thing and redirect to home (which triggers a new auth)
                logger.error("User authentication failed", exc_info=True)
                response = RedirectResponse(url="/")
                await response(scope, receive, send)
                return

            # store token id and access token
            request.session["user"] = dict(user)

            logger.info(f'Storing access token of user "{user["email"]}"...')
            if self.db is None:
                request.session["token"] = dict(token)
            else:
                self.db.put(user["email"], dict(token))

            # finally, redirect to the original path
            path = request.session.pop("original_path", "/")

            response = RedirectResponse(url=path)

        await response(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Middleware entry point, called by starlette."""
        request = Request(scope)

        if request.url.path in self.PUBLIC_PATHS:
            return await self.app(scope, receive, send)

        user = request.session.get("user")

        # no user => start authentication
        if user is None:
            return await self._authenticate(scope, receive, send)

        # fetch the token from the database associated with the user
        if self.db is None:
            token = request.session.get("token")
        else:
            token = self.db.get(user["email"])

        try:
            # check that the token is still valid (e.g. it has not expired)
            if token is None:
                raise logging.error.InvalidTokenError
            await self._client.parse_id_token(request, token)
        except Exception:
            # invalidate session and redirect.
            del request.session["user"]
            if self.db is None:
                del request.session["token"]
            else:
                self.db.delete(user["email"])

            redirect_uri = self._redirect_uri(request)
            response = self._client.authorize_redirect(request, redirect_uri)
            return await (await response)(scope, receive, send)

        logger.info(f'User "{user["email"]}" is authenticated.')

        # user is authenticated, continue to the next middleware
        await self.app(scope, receive, send)
