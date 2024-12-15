"""This is a type hinting file for the authx package."""

import datetime
import sys
from collections.abc import Sequence
from typing import Callable, Literal, Optional, TypeVar, Union

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import ParamSpecKwargs  # pragma: no cover
else:
    from typing_extensions import ParamSpecKwargs  # pragma: no cover


T = TypeVar("T")
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

TokenCallback = Callable[[str, ParamSpecKwargs], bool]
ModelCallback = Callable[[str, ParamSpecKwargs], Optional[T]]
