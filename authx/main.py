"""Main module for AuthX."""

import contextlib
from collections.abc import Awaitable, Coroutine
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
    Union,
    overload,
)

from fastapi import Depends, Request, Response, WebSocket

from authx._internal._callback import _CallbackHandler
from authx._internal._error import _ErrorHandler
from authx._internal._ratelimit import RateLimiter
from authx._internal._scopes import has_required_scopes
from authx._internal._session import SessionInfo
from authx._internal._utils import get_uuid
from authx.config import AuthXConfig
from authx.core import _get_token_from_request
from authx.dependencies import AuthXDependency
from authx.exceptions import (
    AuthXException,
    InsufficientScopeError,
    JWTDecodeError,
    MissingTokenError,
    RevokedTokenError,
)
from authx.schema import RequestToken, TokenPayload, TokenResponse
from authx.types import (
    DateTimeExpression,
    StringOrSequence,
    T,
    TokenLocations,
    TokenType,
)


class AuthX(_CallbackHandler[T], _ErrorHandler):
    """The base class for AuthX.

    AuthX enables JWT management within a FastAPI application.
    Its main purpose is to provide a reusable & simple syntax to protect API
    with JSON Web Token authentication.

    Args:
        config (AuthXConfig, optional): Configuration instance to use. Defaults to AuthXConfig().
        model (Optional[T], optional): Model type hint. Defaults to dict[str, Any].

    Note:
        AuthX is a Generic python object.
        Its TypeVar is not mandatory but helps type hinting furing development

    """

    def __init__(self, config: AuthXConfig = AuthXConfig(), model: Optional[T] = None) -> None:
        """AuthX base object.

        Args:
            config (AuthXConfig, optional): Configuration instance to use. Defaults to AuthXConfig().
            model (Optional[T], optional): Model type hint. Defaults to dict[str, Any].
        """
        self.model: Union[T, dict[str, Any]] = model if model is not None else {}
        super().__init__(model=model)
        super(_CallbackHandler, self).__init__()
        self._config = config
        self._session_store: Optional[Any] = None

    def load_config(self, config: AuthXConfig) -> None:
        """Load and store the configuration for the authentication system.

        Sets the internal configuration object with the provided authentication configuration.

        Args:
            config: The configuration settings for the AuthX authentication system.

        Returns:
            None
        """
        self._config = config

    @property
    def config(self) -> AuthXConfig:
        """AuthX Configuration getter.

        Returns:
            AuthXConfig: Configuration BaseSettings
        """
        return self._config

    def _create_payload(
        self,
        uid: str,
        type: str,
        fresh: bool = False,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        scopes: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> TokenPayload:
        # Handle additional data
        if data is None:
            data = {}
        # Handle expiry date
        exp = expiry
        if exp is None:
            exp = self.config.JWT_ACCESS_TOKEN_EXPIRES if type == "access" else self.config.JWT_REFRESH_TOKEN_EXPIRES
        # Handle CSRF
        csrf = ""
        if self.config.has_location("cookies") and self.config.JWT_COOKIE_CSRF_PROTECT:
            csrf = get_uuid()
        # Handle audience
        aud = audience
        if aud is None:
            aud = self.config.JWT_ENCODE_AUDIENCE
        return TokenPayload(
            sub=uid,
            fresh=fresh,
            exp=exp,
            type=type,
            iss=self.config.JWT_ENCODE_ISSUER,
            aud=aud,
            csrf=csrf,
            scopes=scopes,
            # Handle NBF
            nbf=None,
            **data,
        )

    def _create_token(
        self,
        uid: str,
        type: str,
        fresh: bool = False,
        headers: Optional[dict[str, Any]] = None,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        scopes: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> str:
        payload = self._create_payload(
            uid=uid,
            type=type,
            fresh=fresh,
            expiry=expiry,
            data=data,
            audience=audience,
            scopes=scopes,
            **kwargs,
        )
        return payload.encode(
            key=self.config.private_key,
            algorithm=self.config.JWT_ALGORITHM,
            headers=headers,
            data=data,
        )

    def _decode_token(
        self,
        token: str,
        verify: bool = True,
        audience: Optional[StringOrSequence] = None,
        issuer: Optional[str] = None,
    ) -> TokenPayload:
        try:
            return TokenPayload.decode(
                token=token,
                key=self.config.public_key,
                algorithms=[self.config.JWT_ALGORITHM],
                verify=verify,
                audience=audience or self.config.JWT_DECODE_AUDIENCE,
                issuer=issuer or self.config.JWT_DECODE_ISSUER,
            )
        except JWTDecodeError:
            previous_key = self.config.previous_public_key
            if previous_key is None:
                raise
            return TokenPayload.decode(
                token=token,
                key=previous_key,
                algorithms=[self.config.JWT_ALGORITHM],
                verify=verify,
                audience=audience or self.config.JWT_DECODE_AUDIENCE,
                issuer=issuer or self.config.JWT_DECODE_ISSUER,
            )

    def _set_cookies(
        self,
        token: str,
        type: str,
        response: Response,
        max_age: Optional[int] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if type == "access":
            token_key = self.config.JWT_ACCESS_COOKIE_NAME
            token_path = self.config.JWT_ACCESS_COOKIE_PATH
            csrf_key = self.config.JWT_ACCESS_CSRF_COOKIE_NAME
            csrf_path = self.config.JWT_ACCESS_CSRF_COOKIE_PATH
        elif type == "refresh":
            token_key = self.config.JWT_REFRESH_COOKIE_NAME
            token_path = self.config.JWT_REFRESH_COOKIE_PATH
            csrf_key = self.config.JWT_REFRESH_CSRF_COOKIE_NAME
            csrf_path = self.config.JWT_REFRESH_CSRF_COOKIE_PATH
        else:
            raise ValueError("Token type must be 'access' | 'refresh'")

        # Set cookie
        response.set_cookie(
            key=token_key,
            value=token,
            path=token_path,
            domain=self.config.JWT_COOKIE_DOMAIN,
            samesite=self.config.JWT_COOKIE_SAMESITE,
            secure=self.config.JWT_COOKIE_SECURE,
            httponly=self.config.JWT_COOKIE_HTTP_ONLY,
            max_age=max_age or self.config.JWT_COOKIE_MAX_AGE,
        )
        # Set CSRF
        if self.config.JWT_COOKIE_CSRF_PROTECT and self.config.JWT_CSRF_IN_COOKIES:
            # Set CSRF cookie to be string not None
            csrf = self._decode_token(token=token, verify=True).csrf
            str_csrf = csrf if csrf is not None else ""
            response.set_cookie(
                key=csrf_key,
                value=str_csrf,
                path=csrf_path,
                domain=self.config.JWT_COOKIE_DOMAIN,
                samesite=self.config.JWT_COOKIE_SAMESITE,
                secure=self.config.JWT_COOKIE_SECURE,
                httponly=False,
                max_age=max_age or self.config.JWT_COOKIE_MAX_AGE,
            )

    def _unset_cookies(
        self,
        type: str,
        response: Response,
    ) -> None:
        if type == "access":
            token_key = self.config.JWT_ACCESS_COOKIE_NAME
            token_path = self.config.JWT_ACCESS_COOKIE_PATH
            csrf_key = self.config.JWT_ACCESS_CSRF_COOKIE_NAME
            csrf_path = self.config.JWT_ACCESS_CSRF_COOKIE_PATH
        elif type == "refresh":
            token_key = self.config.JWT_REFRESH_COOKIE_NAME
            token_path = self.config.JWT_REFRESH_COOKIE_PATH
            csrf_key = self.config.JWT_REFRESH_CSRF_COOKIE_NAME
            csrf_path = self.config.JWT_REFRESH_CSRF_COOKIE_PATH
        else:
            raise ValueError("Token type must be 'access' | 'refresh'")
        # Unset cookie
        response.delete_cookie(
            key=token_key,
            path=token_path,
            domain=self.config.JWT_COOKIE_DOMAIN,
        )
        if self.config.JWT_COOKIE_CSRF_PROTECT and self.config.JWT_CSRF_IN_COOKIES:
            response.delete_cookie(
                key=csrf_key,
                path=csrf_path,
                domain=self.config.JWT_COOKIE_DOMAIN,
            )

    @overload
    async def _get_token_from_request(
        self,
        request: Request,
        locations: Optional[TokenLocations] = None,
        refresh: bool = False,
        optional: Literal[False] = False,
    ) -> RequestToken: ...

    @overload
    async def _get_token_from_request(
        self,
        request: Request,
        locations: Optional[TokenLocations] = None,
        refresh: bool = False,
        optional: Literal[True] = True,
    ) -> Optional[RequestToken]: ...

    async def _get_token_from_request(
        self,
        request: Request,
        locations: Optional[TokenLocations] = None,
        refresh: bool = False,
        optional: bool = False,
    ) -> Optional[RequestToken]:
        # Use configured token locations if not explicitly provided
        if locations is None:
            locations = list(self.config.JWT_TOKEN_LOCATION)
        try:
            # Directly call the internal function to get the token
            return await _get_token_from_request(
                request=request,
                refresh=refresh,
                locations=locations,
                config=self.config,
            )
        except MissingTokenError:
            # Return None if optional, else propagate the exception
            if optional:
                return None
            raise

    async def get_access_token_from_request(
        self, request: Request, locations: Optional[TokenLocations] = None
    ) -> RequestToken:
        """Dependency to retrieve access token from request.

        Args:
            request (Request): Request to retrieve access token from
            locations (Optional[TokenLocations], optional): Locations to retrieve token from. Defaults to None.

        Raises:
            MissingTokenError: When no `access` token is available in request

        Returns:
            RequestToken: Request Token instance for `access` token type
        """
        return await self._get_token_from_request(request, optional=False, locations=locations)

    async def get_refresh_token_from_request(
        self, request: Request, locations: Optional[TokenLocations] = None
    ) -> RequestToken:
        """Dependency to retrieve refresh token from request.

        Args:
            request (Request): Request to retrieve refresh token from
            locations (Optional[TokenLocations], optional): Locations to retrieve token from. Defaults to None.

        Raises:
            MissingTokenError: When no `refresh` token is available in request

        Returns:
            RequestToken: Request Token instance for `refresh` token type
        """
        return await self._get_token_from_request(request, refresh=True, optional=False, locations=locations)

    async def _auth_required(
        self,
        request: Request,
        type: str = "access",
        verify_type: bool = True,
        verify_fresh: bool = False,
        verify_csrf: Optional[bool] = None,
        locations: Optional[TokenLocations] = None,
    ) -> TokenPayload:
        if type == "access":
            method = self.get_access_token_from_request
        elif type == "refresh":
            method = self.get_refresh_token_from_request
        else:
            ...  # pragma: no cover
        if verify_csrf is None:
            verify_csrf = self.config.JWT_COOKIE_CSRF_PROTECT and (
                request.method.upper() in self.config.JWT_CSRF_METHODS
            )

        request_token = await method(
            request=request,
            locations=locations,
        )

        if await self.is_token_in_blocklist(request_token.token):
            raise RevokedTokenError("Token has been revoked")

        return self.verify_token(
            request_token,
            verify_type=verify_type,
            verify_fresh=verify_fresh,
            verify_csrf=verify_csrf,
        )

    def verify_token(
        self,
        token: RequestToken,
        verify_type: bool = True,
        verify_fresh: bool = False,
        verify_csrf: bool = True,
    ) -> TokenPayload:
        """Verify a request token.

        Attempts verification with the current key first, then falls back
        to the previous key if key rotation is configured.

        Args:
            token (RequestToken): RequestToken instance
            verify_type (bool, optional): Apply token type verification. Defaults to True.
            verify_fresh (bool, optional): Apply token freshness verification. Defaults to False.
            verify_csrf (bool, optional): Apply token CSRF verification. Defaults to True.

        Returns:
            TokenPayload: Verified token payload
        """
        try:
            return token.verify(
                key=self.config.public_key,
                algorithms=[self.config.JWT_ALGORITHM],
                verify_fresh=verify_fresh,
                verify_type=verify_type,
                verify_csrf=verify_csrf,
                audience=self.config.JWT_DECODE_AUDIENCE,
                issuer=self.config.JWT_DECODE_ISSUER,
            )
        except JWTDecodeError:
            previous_key = self.config.previous_public_key
            if previous_key is None:
                raise
            return token.verify(
                key=previous_key,
                algorithms=[self.config.JWT_ALGORITHM],
                verify_fresh=verify_fresh,
                verify_type=verify_type,
                verify_csrf=verify_csrf,
                audience=self.config.JWT_DECODE_AUDIENCE,
                issuer=self.config.JWT_DECODE_ISSUER,
            )

    def create_access_token(
        self,
        uid: str,
        fresh: bool = False,
        headers: Optional[dict[str, Any]] = None,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        scopes: Optional[list[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Generate an Access Token.

        Args:
            uid (str): Unique identifier to generate token for
            fresh (bool, optional): Generate fresh token. Defaults to False.
            headers (Optional[dict[str, Any]], optional): Custom JWT headers. Defaults to None.
            expiry (Optional[DateTimeExpression], optional): Use a user defined expiry claim. Defaults to None.
            data (Optional[dict[str, Any]], optional): Additional data to store in token. Defaults to None.
            audience (Optional[StringOrSequence], optional): Audience claim. Defaults to None.
            scopes (Optional[list[str]], optional): List of scopes to include in the token. Defaults to None.

        Returns:
            str: Access Token

        Example:
            ```python
            # Token with scopes
            token = auth.create_access_token(
                uid="user123",
                scopes=["users:read", "posts:write"]
            )
            ```
        """
        return self._create_token(
            uid=uid,
            type="access",
            fresh=fresh,
            headers=headers,
            expiry=expiry,
            data=data,
            audience=audience,
            scopes=scopes,
        )

    def create_refresh_token(
        self,
        uid: str,
        headers: Optional[dict[str, Any]] = None,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        scopes: Optional[list[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Generate a Refresh Token.

        Args:
            uid (str): Unique identifier to generate token for
            headers (Optional[dict[str, Any]], optional): Custom JWT headers. Defaults to None.
            expiry (Optional[DateTimeExpression], optional): Use a user defined expiry claim. Defaults to None.
            data (Optional[dict[str, Any]], optional): Additional data to store in token. Defaults to None.
            audience (Optional[StringOrSequence], optional): Audience claim. Defaults to None.
            scopes (Optional[list[str]], optional): List of scopes to include in the token. Defaults to None.

        Returns:
            str: Refresh Token
        """
        return self._create_token(
            uid=uid,
            type="refresh",
            headers=headers,
            expiry=expiry,
            data=data,
            audience=audience,
            scopes=scopes,
        )

    def create_token_pair(
        self,
        uid: str,
        fresh: bool = False,
        headers: Optional[dict[str, Any]] = None,
        access_expiry: Optional[DateTimeExpression] = None,
        refresh_expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        access_scopes: Optional[list[str]] = None,
        refresh_scopes: Optional[list[str]] = None,
    ) -> TokenResponse:
        """Generate an access and refresh token pair.

        Convenience method that creates both tokens at once and returns them
        in a standardized ``TokenResponse`` model.

        Args:
            uid: Unique identifier of the user.
            fresh: Whether the access token should be marked as fresh. Defaults to False.
            headers: Optional custom JWT headers applied to both tokens.
            access_expiry: Optional expiry override for the access token.
            refresh_expiry: Optional expiry override for the refresh token.
            data: Optional additional data stored in both tokens.
            audience: Optional audience claim for both tokens.
            access_scopes: Optional scopes for the access token.
            refresh_scopes: Optional scopes for the refresh token.

        Returns:
            TokenResponse: A model containing ``access_token``, ``refresh_token``, and ``token_type``.

        Example:
            ```python
            tokens = auth.create_token_pair(uid="user123", fresh=True)
            return tokens  # {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}
            ```
        """
        access_token = self.create_access_token(
            uid=uid,
            fresh=fresh,
            headers=headers,
            expiry=access_expiry,
            data=data,
            audience=audience,
            scopes=access_scopes,
        )
        refresh_token = self.create_refresh_token(
            uid=uid,
            headers=headers,
            expiry=refresh_expiry,
            data=data,
            audience=audience,
            scopes=refresh_scopes,
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def set_access_cookies(
        self,
        token: str,
        response: Response,
        max_age: Optional[int] = None,
    ) -> None:
        """Add 'Set-Cookie' for access token in response header.

        Args:
            token (str): Access token
            response (Response): response to set cookie on
            max_age (Optional[int], optional): Max Age cookie parameter. Defaults to None.
        """
        self._set_cookies(token=token, type="access", response=response, max_age=max_age)

    def set_refresh_cookies(
        self,
        token: str,
        response: Response,
        max_age: Optional[int] = None,
    ) -> None:
        """Add 'Set-Cookie' for refresh token in response header.

        Args:
            token (str): Refresh token
            response (Response): response to set cookie on
            max_age (Optional[int], optional): Max Age cookie parameter. Defaults to None.
        """
        self._set_cookies(token=token, type="refresh", response=response, max_age=max_age)

    def unset_access_cookies(
        self,
        response: Response,
    ) -> None:
        """Remove 'Set-Cookie' for access token in response header.

        Args:
            response (Response): response to remove cooke from
        """
        self._unset_cookies("access", response=response)

    def unset_refresh_cookies(
        self,
        response: Response,
    ) -> None:
        """Remove 'Set-Cookie' for refresh token in response header.

        Args:
            response (Response): response to remove cooke from
        """
        self._unset_cookies("refresh", response=response)

    def unset_cookies(
        self,
        response: Response,
    ) -> None:
        """Remove 'Set-Cookie' for tokens from response headers.

        Args:
            response (Response): response to remove token cookies from
        """
        self.unset_access_cookies(response)
        self.unset_refresh_cookies(response)

    # Notes:
    # The AuthXDeps is a utility class, to enable quick token operations
    # within the route logic. It provides methods to avoid additional code
    # in your route that would be outside of the route logic

    # Such methods includes setting and unsetting cookies without the need
    # to generate a response object beforehand.

    @property
    def DEPENDENCY(self) -> AuthXDependency[Any]:
        """FastAPI Dependency to return an AuthX sub-object within the route context."""
        return Depends(self.get_dependency)

    @property
    def BUNDLE(self) -> AuthXDependency[Any]:
        """FastAPI Dependency to return a AuthX sub-object within the route context."""
        return self.DEPENDENCY

    @property
    def FRESH_REQUIRED(self) -> TokenPayload:
        """FastAPI Dependency to enforce valid token availability in request."""
        return Depends(self.fresh_token_required)

    @property
    def ACCESS_REQUIRED(self) -> TokenPayload:
        """FastAPI Dependency to enforce presence of an `access` token in request."""
        return Depends(self.access_token_required)

    @property
    def REFRESH_REQUIRED(self) -> TokenPayload:
        """FastAPI Dependency to enforce presence of a `refresh` token in request."""
        return Depends(self.refresh_token_required)

    @property
    def ACCESS_TOKEN(self) -> RequestToken:
        """FastAPI Dependency to retrieve access token from request."""

        async def _get_access_token(request: Request) -> Optional[RequestToken]:
            return await self._get_token_from_request(request, refresh=False, optional=True)

        return Depends(_get_access_token)

    @property
    def REFRESH_TOKEN(self) -> RequestToken:
        """FastAPI Dependency to retrieve refresh token from request."""

        async def _get_refresh_token(request: Request) -> Optional[RequestToken]:
            return await self._get_token_from_request(request, refresh=True, optional=True)

        return Depends(_get_refresh_token)

    @property
    def CURRENT_SUBJECT(self) -> T:
        """FastAPI Dependency to retrieve the current subject from request."""
        return Depends(self.get_current_subject)

    @property
    def WS_AUTH_REQUIRED(self) -> TokenPayload:
        """FastAPI Dependency to enforce valid access token on a WebSocket connection.

        Extracts the token from the ``token`` query parameter or the ``Authorization``
        header of the WebSocket handshake request.
        """
        return Depends(self._ws_auth_required)

    async def _ws_auth_required(self, websocket: WebSocket) -> TokenPayload:
        """Verify an access token from a WebSocket connection.

        Looks for the token in the query string (``?token=...``) first,
        then falls back to the ``Authorization`` header.

        Raises:
            MissingTokenError: When no token is found.
            JWTDecodeError: When the token is invalid.
        """
        token_str: Optional[str] = websocket.query_params.get(self.config.JWT_QUERY_STRING_NAME)
        if token_str is None:
            auth_header = websocket.headers.get(self.config.JWT_HEADER_NAME)
            if auth_header is not None and self.config.JWT_HEADER_TYPE:
                token_str = auth_header.removeprefix(f"{self.config.JWT_HEADER_TYPE} ")
            elif auth_header is not None:
                token_str = auth_header

        if token_str is None:
            raise MissingTokenError(
                f"Missing token in WebSocket query parameter '{self.config.JWT_QUERY_STRING_NAME}' "
                f"or '{self.config.JWT_HEADER_NAME}' header"
            )

        request_token = RequestToken(token=token_str, csrf=None, type="access", location="query")
        if await self.is_token_in_blocklist(request_token.token):
            raise RevokedTokenError("Token has been revoked")
        return self.verify_token(request_token, verify_type=True, verify_fresh=False, verify_csrf=False)

    def get_dependency(self, request: Request, response: Response) -> AuthXDependency[Any]:
        """FastAPI Dependency to return a AuthX sub-object within the route context.

        Args:
            request (Request): Request context managed by FastAPI
            response (Response): Response context managed by FastAPI

        Note:
            The AuthXDeps is a utility class, to enable quick token operations
            within the route logic. It provides methods to avoid additional code
            in your route that would be outside of the route logic

            Such methods includes setting and unsetting cookies without the need
            to generate a response object beforehand

        Returns:
            AuthXDeps: The contextful AuthX object
        """
        return AuthXDependency(self, request=request, response=response)

    def token_required(
        self,
        type: str = "access",
        verify_type: bool = True,
        verify_fresh: bool = False,
        verify_csrf: Optional[bool] = None,
        locations: Optional[TokenLocations] = None,
    ) -> Callable[[Request], Awaitable[TokenPayload]]:
        """Dependency to enforce valid token availability in request.

        Args:
            type (str, optional): Require a given token type. Defaults to "access".
            verify_type (bool, optional): Apply type verification. Defaults to True.
            verify_fresh (bool, optional): Require token freshness. Defaults to False.
            verify_csrf (Optional[bool], optional): Enable CSRF verification. Defaults to None.
            locations (Optional[TokenLocations], optional): Locations to retrieve token from. Defaults to None.

        Returns:
            Callable[[Request], TokenPayload]: Dependency for Valid token Payload retrieval
        """

        async def _auth_required(request: Request) -> Any:
            return await self._auth_required(
                request=request,
                type=type,
                verify_csrf=verify_csrf,
                verify_type=verify_type,
                verify_fresh=verify_fresh,
                locations=locations,
            )

        return _auth_required

    @property
    def fresh_token_required(self) -> Callable[[Request], Awaitable[TokenPayload]]:
        """FastAPI Dependency to enforce presence of a `fresh` `access` token in request."""
        return self.token_required(
            type="access",
            verify_csrf=None,
            verify_fresh=True,
            verify_type=True,
        )

    @property
    def access_token_required(self) -> Callable[[Request], Awaitable[TokenPayload]]:
        """FastAPI Dependency to enforce presence of an `access` token in request."""
        return self.token_required(
            type="access",
            verify_csrf=None,
            verify_fresh=False,
            verify_type=True,
        )

    @property
    def refresh_token_required(self) -> Callable[[Request], Awaitable[TokenPayload]]:
        """FastAPI Dependency to enforce presence of a `refresh` token in request."""
        return self.token_required(
            type="refresh",
            verify_csrf=None,
            verify_fresh=False,
            verify_type=True,
        )

    def scopes_required(
        self,
        *scopes: str,
        all_required: bool = True,
        verify_type: bool = True,
        verify_fresh: bool = False,
        verify_csrf: Optional[bool] = None,
        locations: Optional[TokenLocations] = None,
    ) -> Callable[[Request], Awaitable[TokenPayload]]:
        """Dependency to enforce required scopes in token.

        Creates a FastAPI dependency that validates that the token contains
        the required scopes. Supports both simple and hierarchical scopes
        with wildcard matching (e.g., "admin:*" matches "admin:users").

        Args:
            *scopes: Variable number of scope strings required.
            all_required: If True (default), ALL scopes must be present (AND logic).
                         If False, at least ONE scope must be present (OR logic).
            verify_type: Apply token type verification. Defaults to True.
            verify_fresh: Require token freshness. Defaults to False.
            verify_csrf: Enable CSRF verification. Defaults to None (uses config).
            locations: Locations to retrieve token from. Defaults to None.

        Returns:
            Callable[[Request], Awaitable[TokenPayload]]: Dependency for scope validation.

        Raises:
            InsufficientScopeError: When token lacks required scopes.

        Example:
            ```python
            # Require single scope
            @app.get("/users", dependencies=[Depends(auth.scopes_required("users:read"))])
            async def list_users(): ...

            # Require multiple scopes (AND)
            @app.delete("/users/{id}", dependencies=[Depends(auth.scopes_required("users:read", "users:delete"))])
            async def delete_user(id: int): ...

            # Require any of the scopes (OR)
            @app.get("/admin", dependencies=[Depends(auth.scopes_required("admin", "superuser", all_required=False))])
            async def admin_panel(): ...

            # Wildcard scope
            @app.get("/admin/users", dependencies=[Depends(auth.scopes_required("admin:*"))])
            async def admin_users(): ...
            ```
        """
        required_scopes = list(scopes)

        async def _scopes_required(request: Request) -> TokenPayload:
            payload = await self._auth_required(
                request=request,
                type="access",
                verify_type=verify_type,
                verify_fresh=verify_fresh,
                verify_csrf=verify_csrf,
                locations=locations,
            )

            if not has_required_scopes(required_scopes, payload.scopes, all_required=all_required):
                raise InsufficientScopeError(required=required_scopes, provided=payload.scopes)

            return payload

        return _scopes_required

    async def get_current_subject(self, request: Request) -> Optional[T]:
        """Retrieve the currently authenticated subject from the request.

        Validates the request token and fetches the corresponding subject based on the user identifier.

        Args:
            request: The HTTP request containing authentication credentials.

        Returns:
            The authenticated subject if present, otherwise None.
        """
        token: TokenPayload = await self._auth_required(request=request)
        uid = token.sub
        return await self._get_current_subject(uid=uid)

    @overload
    async def get_token_from_request(
        self,
        request: Request,
        type: TokenType = "access",
        optional: Literal[True] = True,
        locations: Optional[TokenLocations] = None,
    ) -> Optional[RequestToken]: ...

    @overload
    async def get_token_from_request(
        self,
        request: Request,
        type: TokenType = "access",
        optional: Literal[False] = False,
        locations: Optional[TokenLocations] = None,
    ) -> RequestToken: ...

    async def get_token_from_request(
        self,
        request: Request,
        type: TokenType = "access",
        optional: bool = True,
        locations: Optional[TokenLocations] = None,
    ) -> Optional[RequestToken]:
        """Retrieve token from request.

        Args:
            request (Request): The FastAPI request object.
            type (TokenType, optional): The type of token to retrieve from request.
                Defaults to "access".
            optional (bool, optional): Whether or not to enforce token presence in request.
                Defaults to True.
            locations (Optional[TokenLocations], optional): Locations to retrieve token from.
                Defaults to None (uses configured JWT_TOKEN_LOCATION).

        Note:
            When `optional=True`, the return value might be `None`
            if no token is available in request.

            When `optional=False`, raises a MissingTokenError.

        Returns:
            Optional[RequestToken]: The RequestToken if available, None if optional and not found.

        Example:
            ```python
            token = await auth.get_token_from_request(request)
            token = await auth.get_token_from_request(request, type="refresh")
            token = await auth.get_token_from_request(request, optional=False)
            ```
        """
        if optional:
            return await self._get_token_from_request(
                request,
                locations=locations,
                refresh=(type == "refresh"),
                optional=True,
            )
        else:
            return await self._get_token_from_request(
                request,
                locations=locations,
                refresh=(type == "refresh"),
                optional=False,
            )

    def _implicit_refresh_enabled_for_request(self, request: Request) -> bool:
        """Check if a request should implement implicit token refresh.

        Args:
            request (Request): Request to check

        Returns:
            bool: True if request allows for refreshing access token
        """
        if request.url.components.path in self.config.JWT_IMPLICIT_REFRESH_ROUTE_EXCLUDE:
            return False
        elif request.url.components.path in self.config.JWT_IMPLICIT_REFRESH_ROUTE_INCLUDE:
            return True
        elif request.method in self.config.JWT_IMPLICIT_REFRESH_METHOD_EXCLUDE:
            return False
        elif request.method in self.config.JWT_IMPLICIT_REFRESH_METHOD_INCLUDE:
            return False
        else:
            return True

    async def implicit_refresh_middleware(
        self,
        request: Request,
        call_next: Callable[[Request], Coroutine[Any, Any, Response]],
    ) -> Response:
        """FastAPI Middleware to enable token refresh for an APIRouter.

        Args:
            request (Request): Incoming request
            call_next (Coroutine): Endpoint logic to be called

        Note:
            This middleware is only based on `access` tokens.
            Using implicit refresh mechanism makes use of `refresh`
            tokens unnecessary.

        Note:
            The refreshed `access` token will not be considered as
            `fresh`

        Note:
            The implicit refresh mechanism is only enabled
            for authorization through cookies.

        Returns:
            Response: Response with update access token cookie if relevant
        """
        response = await call_next(request)

        if self.config.has_location("cookies") and self._implicit_refresh_enabled_for_request(request):
            with contextlib.suppress(AuthXException):
                # Refresh mechanism
                token = await self._get_token_from_request(
                    request=request,
                    locations=["cookies"],
                    refresh=False,
                    optional=False,
                )
                payload = self.verify_token(token, verify_fresh=False, verify_csrf=False)
                if payload.time_until_expiry < self.config.JWT_IMPLICIT_REFRESH_DELTATIME:
                    new_token = self.create_access_token(uid=payload.sub, fresh=False, data=payload.extra_dict)
                    self.set_access_cookies(new_token, response=response)
        return response

    def rate_limited(
        self,
        max_requests: int = 10,
        window: int = 60,
        key_func: Optional[Callable[[Request], str]] = None,
    ) -> Callable[[Request], Awaitable[TokenPayload]]:
        """Dependency combining rate limiting with access token verification.

        Args:
            max_requests: Maximum requests allowed within the window.
            window: Time window in seconds.
            key_func: Callable to extract rate limit key from request. Defaults to client IP.

        Returns:
            A FastAPI dependency that enforces both rate limiting and token auth.

        Example:
            ```python
            @app.get("/api", dependencies=[Depends(auth.rate_limited(max_requests=5, window=60))])
            async def api_route(): ...
            ```
        """
        limiter = RateLimiter(max_requests=max_requests, window=window, key_func=key_func)

        async def _rate_limited_auth(request: Request) -> TokenPayload:
            await limiter(request)
            return await self._auth_required(request=request)

        return _rate_limited_auth

    # --- Session Management ---

    def set_session_store(self, store: Any) -> None:
        """Register a session storage backend.

        Args:
            store: An object implementing the ``SessionStoreProtocol``.
        """
        self._session_store = store

    async def create_session(
        self,
        uid: str,
        request: Optional[Request] = None,
        device_info: Optional[dict[str, Any]] = None,
    ) -> SessionInfo:
        """Create a new session and persist it via the session store.

        Args:
            uid: User identifier.
            request: Optional HTTP request for IP/User-Agent extraction.
            device_info: Optional additional device metadata.

        Returns:
            The created ``SessionInfo`` instance.
        """
        ip_address: Optional[str] = None
        user_agent: Optional[str] = None
        if request is not None:
            if request.client is not None:
                ip_address = request.client.host
            user_agent = request.headers.get("user-agent")

        session = SessionInfo(
            uid=uid,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
        )

        if self._session_store is not None:
            await self._session_store.create(session)

        return session

    async def list_sessions(self, uid: str) -> list[SessionInfo]:
        """List all active sessions for a user.

        Args:
            uid: User identifier.

        Returns:
            List of active ``SessionInfo`` objects.
        """
        if self._session_store is None:
            return []
        return await self._session_store.list_by_user(uid)

    async def revoke_session(self, session_id: str) -> None:
        """Revoke a single session by ID.

        Args:
            session_id: The session to revoke.
        """
        if self._session_store is not None:
            await self._session_store.delete(session_id)

    async def revoke_all_sessions(self, uid: str) -> None:
        """Revoke all sessions for a user.

        Args:
            uid: User identifier.
        """
        if self._session_store is not None:
            await self._session_store.delete_all_by_user(uid)

    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Retrieve a session by ID.

        Args:
            session_id: The session to look up.

        Returns:
            The ``SessionInfo`` if found and active, otherwise None.
        """
        if self._session_store is None:
            return None
        return await self._session_store.get(session_id)
