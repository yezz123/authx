import logging

from authlib.integrations import starlette_client
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class MiddlewareOauth2:
    """Middleware for authentication through Oauth2.
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

        self._client = starlette_client.OAuth(
            starlette_client.StarletteRemoteApp("starlette"),
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
        if scheme == "http" and self._force_https_redirect:  # pragma: no cover
            scheme = "https"  # pragma: no cover
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
            logger.info("Fetching id token...")  # pragma: no cover
            # try to construct a user from the access token
            try:  # pragma: no cover
                token = await self._client.authorize_access_token(
                    request
                )  # pragma: no cover
                user = await self._client.parse_id_token(
                    request, token
                )  # pragma: no cover
                assert user is not None  # pragma: no cover
            except Exception as e:  # pragma: no cover
                # impossible to build a user => invalidate the whole thing and redirect to home (which triggers a new auth)
                logger.error(
                    "User authentication failed", exc_info=True
                )  # pragma: no cover
                response = RedirectResponse(url="/")  # pragma: no cover
                await response(scope, receive, send)  # pragma: no cover
                return  # pragma: no cover

            # store token id and access token
            request.session["user"] = dict(user)  # pragma: no cover

            logger.info(
                f'Storing access token of user "{user["email"]}"...'
            )  # pragma: no cover
            if self.db is None:  # pragma: no cover
                request.session["token"] = dict(token)  # pragma: no cover
            else:  # pragma: no cover
                self.db.put(user["email"], dict(token))  # pragma: no cover

            # finally, redirect to the original path
            path = request.session.pop("original_path", "/")  # pragma: no cover

            response = RedirectResponse(url=path)  # pragma: no cover

        await response(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Middleware entry point, called by starlette.

        Args:
            scope (Scope): The scope of the request.
            receive (Receive): The receive channel.
            send (Send): The send channel.

        Raises:
            logging.error.InvalidTokenError: If the token is invalid.
        """
        request = Request(scope)

        if request.url.path in self.PUBLIC_PATHS:
            return await self.app(scope, receive, send)  # pragma: no cover

        user = request.session.get("user")

        # no user => start authentication
        if user is None:
            return await self._authenticate(scope, receive, send)

        # fetch the token from the database associated with the user
        if self.db is None:  # pragma: no cover
            token = request.session.get("token")  # pragma: no cover
        else:  # pragma: no cover
            token = self.db.get(user["email"])  # pragma: no cover

        try:  # pragma: no cover
            # check that the token is still valid (e.g. it has not expired)
            if token is None:  # pragma: no cover
                raise logging.error.InvalidTokenError  # pragma: no cover
            await self._client.parse_id_token(request, token)  # pragma: no cover
        except Exception as e:  # pragma: no cover
            # invalidate session and redirect.
            del request.session["user"]  # pragma: no cover
            if self.db is None:  # pragma: no cover
                del request.session["token"]  # pragma: no cover
            else:  # pragma: no cover
                self.db.delete(user["email"])  # pragma: no cover

            redirect_uri = self._redirect_uri(request)  # pragma: no cover
            response = self._client.authorize_redirect(
                request, redirect_uri
            )  # pragma: no cover
            return await (await response)(scope, receive, send)  # pragma: no cover

        logger.info(f'User "{user["email"]}" is authenticated.')  # pragma: no cover

        # user is authenticated, continue to the next middleware
        await self.app(scope, receive, send)  # pragma: no cover
