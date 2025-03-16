"""Token encoding and decoding functions."""

import datetime
import warnings
from collections.abc import Sequence
from typing import Any, Optional, Union

import jwt

from authx._internal._utils import RESERVED_CLAIMS, get_now, get_now_ts, get_uuid
from authx.exceptions import AuthxArgumentDeprecationWarning, JWTDecodeError
from authx.types import (
    AlgorithmType,
    DateTimeExpression,
    Numeric,
    StringOrSequence,
    TokenType,
)


def create_token(
    uid: str,
    key: str,
    type: TokenType = "access",
    jti: Optional[str] = None,
    expiry: Optional[DateTimeExpression] = None,
    issued: Optional[Union[Numeric, DateTimeExpression]] = None,
    fresh: bool = False,
    csrf: Optional[str] = None,
    algorithm: AlgorithmType = "HS256",
    headers: Optional[dict[str, Any]] = None,
    audience: Optional[StringOrSequence] = None,
    issuer: Optional[str] = None,
    additional_data: Optional[dict[str, Any]] = None,
    not_before: Optional[Union[Union[float, int], DateTimeExpression]] = None,
    data: Optional[dict[str, Any]] = None,
    ignore_errors: bool = True,
) -> str:
    """Encode a token."""
    now = get_now()

    # Filter additional data to remove JWT claims
    additional_claims = {}
    if additional_data is not None:
        if not ignore_errors and set(additional_data.keys()).intersection(RESERVED_CLAIMS):
            raise ValueError(f"{RESERVED_CLAIMS} are forbidden in additional claims")
        additional_claims = {k: v for k, v in additional_data.items() if k not in RESERVED_CLAIMS}

    jwt_claims: dict[str, Union[str, bool, float, int, Sequence[str]]] = {
        "sub": uid,
        "jti": jti or get_uuid(),
        "type": type,
    }

    if type == "access":
        jwt_claims["fresh"] = fresh

    if csrf and not isinstance(csrf, str):
        jwt_claims["csrf"] = get_uuid()
    elif isinstance(csrf, str):
        jwt_claims["csrf"] = csrf

    if isinstance(issued, datetime.datetime):
        jwt_claims["iat"] = issued.timestamp()
    elif isinstance(issued, (float, int)):
        jwt_claims["iat"] = issued
    else:
        jwt_claims["iat"] = get_now_ts()

    if isinstance(expiry, datetime.datetime):
        jwt_claims["exp"] = expiry.timestamp()
    elif isinstance(expiry, datetime.timedelta):
        jwt_claims["exp"] = (now + expiry).timestamp()
    elif isinstance(expiry, (float, int)):
        jwt_claims["exp"] = expiry

    if audience:
        jwt_claims["aud"] = audience
    if issuer:
        jwt_claims["iss"] = issuer

    if isinstance(not_before, datetime.datetime):
        jwt_claims["nbf"] = not_before.timestamp()
    elif isinstance(not_before, datetime.timedelta):
        jwt_claims["nbf"] = (now + not_before).timestamp()
    elif isinstance(not_before, (int, float)):
        jwt_claims["nbf"] = not_before

    if data:
        jwt_claims.update(data)

    payload = additional_claims | jwt_claims

    return jwt.encode(payload=payload, key=key, algorithm=algorithm, headers=headers)


def decode_token(
    token: str,
    key: str,
    algorithms: Optional[Sequence[AlgorithmType]] = None,
    audience: Optional[StringOrSequence] = None,
    issuer: Optional[str] = None,
    verify: bool = True,
    data: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Decode a token."""
    if data is not None:
        warnings.warn(
            "passing data keyword argument to decode_token() is deprecated and will be removed in authx version 2.",
            AuthxArgumentDeprecationWarning,
            stacklevel=2,
        )

    # Default to HS256 if no algorithms are provided
    if algorithms is None:  # pragma: no cover
        algorithms = ["HS256"]  # pragma: no cover
    # Explicitly cast algorithms to list[str]
    # to avoid mypy error: "Value of type "Optional[Sequence[AlgorithmType]]" is not indexable"
    algorithm: list[str] = list(algorithms) if algorithms else ["HS256"]
    try:
        return jwt.decode(
            jwt=token,
            key=key,
            algorithms=algorithm,
            audience=audience,
            issuer=issuer,
            options={"verify_signature": verify},
        )
    except Exception as e:
        raise JWTDecodeError(*e.args) from e
