"""AuthX Configuration Module."""

from collections.abc import Sequence
from datetime import timedelta
from typing import Optional

from jwt.algorithms import get_default_algorithms, requires_cryptography
from pydantic import Field
from pydantic.version import VERSION as PYDANTIC_VERSION

from authx.exceptions import BadConfigurationError
from authx.types import (
    AlgorithmType,
    HTTPMethods,
    SameSitePolicy,
    StringOrSequence,
    TokenLocations,
)

if PYDANTIC_V2 := PYDANTIC_VERSION.startswith("2."):
    from pydantic_settings import BaseSettings  # pragma: no cover
else:
    from pydantic import BaseSettings  # type: ignore # pragma: no cover


class AuthXConfig(BaseSettings):
    """AuthX Base Configuration Object.

    Args:
        BaseSettings (BaseSettings): BaseSettings class from Pydantic

    Raises:
        BadConfigurationError: If JWT_ALGORITHM is not supported
        BadConfigurationError: If JWT_ALGORITHM requires a key and it is not set

    Returns:
        AuthXConfig: AuthX Configuration Object
    """

    JWT_ACCESS_TOKEN_EXPIRES: Optional[timedelta] = timedelta(minutes=15)
    JWT_ALGORITHM: AlgorithmType = "HS256"
    JWT_DECODE_ALGORITHMS: Sequence[AlgorithmType] = Field(default_factory=lambda: ["HS256"])  # type: ignore
    JWT_DECODE_AUDIENCE: Optional[StringOrSequence] = None
    JWT_DECODE_ISSUER: Optional[str] = None
    JWT_DECODE_LEEWAY: Optional[int] = 0
    JWT_ENCODE_AUDIENCE: Optional[StringOrSequence] = None
    JWT_ENCODE_ISSUER: Optional[str] = None
    JWT_ENCODE_NBF: bool = True
    JWT_ERROR_MESSAGE_KEY: str = "msg"
    JWT_IDENTITY_CLAIM: str = "sub"
    JWT_PRIVATE_KEY: Optional[str] = None
    JWT_PUBLIC_KEY: Optional[str] = None
    JWT_REFRESH_TOKEN_EXPIRES: Optional[timedelta] = timedelta(days=20)
    JWT_SECRET_KEY: Optional[str] = None
    JWT_TOKEN_LOCATION: TokenLocations = Field(default_factory=lambda: ["headers"])  # type: ignore
    # Header Options
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"
    # Cookies Options
    JWT_ACCESS_COOKIE_NAME: str = "access_token_cookie"
    JWT_ACCESS_COOKIE_PATH: str = "/"
    JWT_COOKIE_CSRF_PROTECT: bool = True
    JWT_COOKIE_DOMAIN: Optional[str] = None
    JWT_COOKIE_MAX_AGE: Optional[int] = None
    JWT_COOKIE_SAMESITE: Optional[SameSitePolicy] = "lax"
    JWT_COOKIE_SECURE: bool = True
    JWT_REFRESH_COOKIE_NAME: str = "refresh_token_cookie"
    JWT_REFRESH_COOKIE_PATH: str = "/"
    JWT_SESSION_COOKIE: bool = True
    # CSRF Options
    JWT_ACCESS_CSRF_COOKIE_NAME: str = "csrf_access_token"
    JWT_ACCESS_CSRF_COOKIE_PATH: str = "/"
    JWT_ACCESS_CSRF_FIELD_NAME: str = "csrf_token"
    JWT_ACCESS_CSRF_HEADER_NAME: str = "X-CSRF-TOKEN"
    JWT_CSRF_CHECK_FORM: bool = False
    JWT_CSRF_IN_COOKIES: bool = True
    JWT_CSRF_METHODS: HTTPMethods = Field(default_factory=lambda: ["POST", "PUT", "PATCH", "DELETE"])  # type: ignore
    JWT_REFRESH_CSRF_COOKIE_NAME: str = "csrf_refresh_token"
    JWT_REFRESH_CSRF_COOKIE_PATH: str = "/"
    JWT_REFRESH_CSRF_FIELD_NAME: str = "csrf_token"
    JWT_REFRESH_CSRF_HEADER_NAME: str = "X-CSRF-TOKEN"
    # Query Options
    JWT_QUERY_STRING_NAME: str = "token"
    # JSON Option
    JWT_JSON_KEY: str = "access_token"
    JWT_REFRESH_JSON_KEY: str = "refresh_token"

    # Implicit Refresh Options
    JWT_IMPLICIT_REFRESH_ROUTE_EXCLUDE: list[str] = Field(default_factory=list)
    JWT_IMPLICIT_REFRESH_ROUTE_INCLUDE: list[str] = Field(default_factory=list)
    JWT_IMPLICIT_REFRESH_METHOD_EXCLUDE: HTTPMethods = Field(default_factory=list)
    JWT_IMPLICIT_REFRESH_METHOD_INCLUDE: HTTPMethods = Field(default_factory=list)
    JWT_IMPLICIT_REFRESH_DELTATIME: timedelta = timedelta(minutes=10)

    @property
    def is_algo_symmetric(self) -> bool:
        """Check if the JWT_ALGORITHM is a symmetric encryption algorithm."""
        return self.JWT_ALGORITHM in get_default_algorithms() and self.JWT_ALGORITHM not in requires_cryptography

    @property
    def is_algo_asymmetric(self) -> bool:
        """Check if the JWT_ALGORITHM is an asymmetric encryption algorithm."""
        return self.JWT_ALGORITHM in get_default_algorithms() and self.JWT_ALGORITHM in requires_cryptography

    def _get_key(self, crypto_value: Optional[str]) -> str:
        """Get the key for the algorithm type (symmetric or asymmetric) and the algorithm."""
        if self.is_algo_symmetric:
            key = self.JWT_SECRET_KEY
        elif self.is_algo_asymmetric:
            key = crypto_value
        else:
            raise BadConfigurationError(
                f"JWT_ALGORITHM {self.JWT_ALGORITHM} is not supported, please use one of {get_default_algorithms()}",
            )

        if key is None:
            raise BadConfigurationError(
                f"JWT_ALGORITHM {self.JWT_ALGORITHM} requires a key, please set JWT_SECRET_KEY or JWT_PUBLIC_KEY and JWT_PRIVATE_KEY",
            )
        return key

    def has_location(self, location: str) -> bool:
        """Check if the token location is enabled."""
        return location in self.JWT_TOKEN_LOCATION

    @property
    def private_key(self) -> str:
        """Private key to encode token."""
        return self._get_key(self.JWT_PRIVATE_KEY)

    @property
    def public_key(self) -> str:
        """Public key to decode token."""
        return self._get_key(self.JWT_PUBLIC_KEY)
