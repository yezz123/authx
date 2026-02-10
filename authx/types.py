"""This is a type hinting file for the authx package."""

import datetime
import sys
from collections.abc import Awaitable, Sequence
from typing import Any, Literal, Optional, Protocol, TypeVar, Union

if sys.version_info >= (3, 10):  # pragma: no cover
    pass  # pragma: no cover
else:
    pass  # pragma: no cover


T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
Numeric = Union[float, int]
ObjectOrSequence = Union[T, Sequence[T]]
StringOrSequence = ObjectOrSequence[str]


DateTimeExpression = Union[datetime.datetime, datetime.timedelta]

SymmetricAlgorithmType = Literal[
    "HS256",
    "HS384",
    "HS512",
]
AsymmetricAlgorithmType = Literal[
    "ES256",
    "ES256K",
    "ES384",
    "ES512",
    "RS256",
    "RS384",
    "RS512",
    "PS256",
    "PS384",
    "PS512",
]
AlgorithmType = Union[SymmetricAlgorithmType, AsymmetricAlgorithmType]


HTTPMethod = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
HTTPMethods = Sequence[HTTPMethod]
SameSitePolicy = Literal["lax", "strict", "none"]
TokenType = Literal["access", "refresh"]
TokenLocation = Literal["headers", "cookies", "json", "query"]
TokenLocations = Sequence[TokenLocation]


class TokenCallback(Protocol):
    """Protocol for token blocklist check callbacks (sync or async)."""

    def __call__(self, token: str, **kwargs: Any) -> Union[bool, Awaitable[bool]]:
        """Check if token is in blocklist."""
        ...


class ModelCallback(Protocol[T_co]):
    """Protocol for model/subject retrieval callbacks (sync or async)."""

    def __call__(self, uid: str, **kwargs: Any) -> Union[Optional[T_co], Awaitable[Optional[T_co]]]:
        """Retrieve model/subject from UID."""
        ...
