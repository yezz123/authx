"""AuthX dependencies for FastAPI."""

from typing import TYPE_CHECKING, Any, Generic, Optional

from fastapi import Request, Response

from authx.types import DateTimeExpression, StringOrSequence, T

if TYPE_CHECKING:
    from authx.main import AuthX


class AuthXDependency(Generic[T]):
    """A dependency class for managing authentication-related operations within a request-response context.

    Provides a convenient interface for creating tokens, setting and unsetting cookies, and retrieving the current authenticated subject.

    Attributes:
        request: The HTTP request associated with the current authentication context.
        response: The HTTP response associated with the current authentication context.

    Methods:
        create_access_token: Generate an access token for a given user.
        create_refresh_token: Generate a refresh token for a given user.
        set_access_cookies: Set access token cookies in the response.
        set_refresh_cookies: Set refresh token cookies in the response.
        unset_access_cookies: Remove access token cookies from the response.
        unset_refresh_cookies: Remove refresh token cookies from the response.
        unset_cookies: Remove all authentication-related cookies from the response.
        get_current_subject: Asynchronously retrieve the currently authenticated subject.
    """

    def __init__(
        self,
        _from: "AuthX[T]",
        request: Request,
        response: Response,
    ) -> None:
        """Initialize the authentication dependency with request, response, and security context.

        Sets up the core components required for managing authentication operations within the current request-response cycle.

        Args:
            _from: The AuthX instance managing authentication mechanisms.
            request: The incoming HTTP request object.
            response: The HTTP response object to be potentially modified during authentication.
        """
        self._response = response
        self._request = request
        self._security = _from

    @property
    def request(self) -> Request:
        """Retrieve the HTTP request associated with the current authentication context.

        Provides read-only access to the request object used during authentication processing.

        Returns:
            The HTTP request object stored in the authentication dependency.
        """
        return self._request

    @property
    def response(self) -> Response:
        """Retrieve the HTTP response associated with the current authentication context.

        Provides read-only access to the response object used during authentication processing.

        Returns:
            The HTTP response object stored in the authentication dependency.
        """
        return self._response

    def create_access_token(
        self,
        uid: str,
        fresh: bool = False,
        headers: Optional[dict[str, Any]] = None,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Generate an access token for a specific user with customizable parameters.

        Delegates token creation to the underlying security mechanism with flexible configuration options.

        Args:
        uid: Unique identifier of the user for whom the token is being created.
        fresh: Flag indicating whether the token should be marked as a fresh authentication.
        headers: Optional custom headers to include in the token.
        expiry: Optional expiration time for the token.
        data: Optional additional data to be encoded in the token.
        audience: Optional target audience for the token.
        *args: Variable positional arguments for additional flexibility.
        **kwargs: Variable keyword arguments for additional configuration.

        Returns:
        A string representing the generated access token.
        """
        return self._security.create_access_token(uid, fresh, headers, expiry, data, audience, *args, **kwargs)

    def create_refresh_token(
        self,
        uid: str,
        headers: Optional[dict[str, Any]] = None,
        expiry: Optional[DateTimeExpression] = None,
        data: Optional[dict[str, Any]] = None,
        audience: Optional[StringOrSequence] = None,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Generate a refresh token for a specific user with customizable parameters.

        Delegates refresh token creation to the underlying security mechanism with flexible configuration options.

        Args:
        uid: Unique identifier of the user for whom the refresh token is being created.
        headers: Optional custom headers to include in the token.
        expiry: Optional expiration time for the token.
        data: Optional additional data to be encoded in the token.
        audience: Optional target audience for the token.
        *args: Variable positional arguments for additional flexibility.
        **kwargs: Variable keyword arguments for additional configuration.

        Returns:
        A string representing the generated refresh token.
        """
        return self._security.create_refresh_token(uid, headers, expiry, data, audience, *args, **kwargs)

    def set_access_cookies(
        self,
        token: str,
        response: Optional[Response] = None,
        max_age: Optional[int] = None,
    ) -> None:
        """Set access token cookies in the HTTP response.

        Configures the response with access token cookies, using the provided token and optional parameters.

        Args:
        token: The access token to be set as a cookie.
        response: Optional HTTP response object to set cookies on. Defaults to the stored response if not provided.
        max_age: Optional maximum age for the cookie before expiration.

        Returns:
        None
        """
        self._security.set_access_cookies(token=token, response=(response or self._response), max_age=max_age)

    def set_refresh_cookies(
        self,
        token: str,
        response: Optional[Response] = None,
        max_age: Optional[int] = None,
    ) -> None:
        """Set refresh token cookies in the HTTP response.

        Configures the response with refresh token cookies, using the provided token and optional parameters.

        Args:
        token: The refresh token to be set as a cookie.
        response: Optional HTTP response object to set cookies on. Defaults to the stored response if not provided.
        max_age: Optional maximum age for the cookie before expiration.

        Returns:
        None
        """
        self._security.set_refresh_cookies(token=token, response=(response or self._response), max_age=max_age)

    def unset_access_cookies(self, response: Optional[Response] = None) -> None:
        """Remove access token cookies from the HTTP response.

        Clears the access token cookies from the specified or default response object.

        Args:
        response: Optional HTTP response object to remove cookies from. Defaults to the stored response if not provided.

        Returns:
        None
        """
        self._security.unset_access_cookies(response=(response or self._response))

    def unset_refresh_cookies(self, response: Optional[Response] = None) -> None:
        """Remove refresh token cookies from the HTTP response.

        Clears the refresh token cookies from the specified or default response object.

        Args:
        response: Optional HTTP response object to remove cookies from. Defaults to the stored response if not provided.

        Returns:
        None
        """
        self._security.unset_access_cookies(response=(response or self._response))

    def unset_cookies(self, response: Optional[Response] = None) -> None:
        """Remove all authentication-related cookies from the HTTP response.

        Clears both access and refresh token cookies from the specified or default response object.

        Args:
        response: Optional HTTP response object to remove cookies from. Defaults to the stored response if not provided.

        Returns:
        None
        """
        self._security.unset_cookies(response=(response or self._response))

    async def get_current_subject(self) -> Optional[T]:
        """Retrieve the currently authenticated subject from the request.

        Asynchronously fetches the authenticated user or subject based on the current request context.

        Returns:
        The authenticated subject if present, otherwise None.
        """
        return await self._security.get_current_subject(request=self._request)
