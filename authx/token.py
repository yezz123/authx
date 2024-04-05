import datetime
from typing import Any, Dict, Optional, Sequence, Union

import jwt

from authx._internal._utils import RESERVED_CLAIMS, get_now, get_now_ts, get_uuid
from authx.exceptions import JWTDecodeError
from authx.types import AlgorithmType, DateTimeExpression, StringOrSequence, TokenType


def create_token(
    uid: str,
    key: str,
    type: TokenType,
    jti: Optional[str] = None,
    expiry: Optional[DateTimeExpression] = None,
    issued: Optional[DateTimeExpression] = None,
    fresh: bool = False,
    csrf: Union[str, bool] = True,
    algorithm: AlgorithmType = "HS256",
    headers: Optional[Dict[str, Any]] = None,
    audience: Optional[StringOrSequence] = None,
    issuer: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None,
    not_before: Optional[Union[int, DateTimeExpression]] = None,
    ignore_errors: bool = True,
) -> str:
    """Encode a token"""
    now = get_now()

    # Filter additional data to remove JWT claims
    additional_claims = {}
    if additional_data is not None:
        if not ignore_errors and set(additional_data.keys()).intersection(
            RESERVED_CLAIMS
        ):
            raise ValueError(f"{RESERVED_CLAIMS} are forbidden in additional claims")
        additional_claims = {
            k: v for k, v in additional_data.items() if k not in RESERVED_CLAIMS
        }

    jwt_claims = {"sub": uid, "jti": jti or get_uuid(), "type": type}

    if type == "access":
        jwt_claims["fresh"] = str(fresh)

    if csrf and not isinstance(csrf, str):
        jwt_claims["csrf"] = get_uuid()
    elif isinstance(csrf, str):
        jwt_claims["csrf"] = csrf

    if isinstance(issued, datetime.datetime):
        jwt_claims["iat"] = issued.timestamp()  # type: ignore
    elif isinstance(issued, (float, int)):
        jwt_claims["iat"] = issued
    else:
        jwt_claims["iat"] = get_now_ts()  # type: ignore

    if isinstance(expiry, datetime.datetime):
        jwt_claims["exp"] = expiry.timestamp()  # type: ignore
    elif isinstance(expiry, datetime.timedelta):
        jwt_claims["exp"] = (now + expiry).timestamp()  # type: ignore
    elif isinstance(expiry, (float, int)):
        jwt_claims["exp"] = expiry

    if audience:
        jwt_claims["aud"] = audience  # type: ignore
    if issuer:
        jwt_claims["iss"] = issuer

    if isinstance(not_before, datetime.datetime):
        jwt_claims["nbf"] = not_before.timestamp()  # type: ignore
    elif isinstance(not_before, datetime.timedelta):
        jwt_claims["nbf"] = (now + not_before).timestamp()  # type: ignore
    elif isinstance(not_before, (int, float)):
        jwt_claims["nbf"] = not_before  # type: ignore

    payload = {**additional_claims, **jwt_claims}

    return jwt.encode(payload=payload, key=key, algorithm=algorithm, headers=headers)


def decode_token(
    token: str,
    key: str,
    algorithms: Optional[Sequence[AlgorithmType]] = None,
    audience: Optional[StringOrSequence] = None,
    issuer: Optional[str] = None,
    verify: bool = True,
) -> Dict[str, Any]:
    """Decode a token"""
    try:
        return jwt.decode(
            jwt=token,
            key=key,
            algorithms=algorithms if algorithms is not None else ["HS256"],  # type: ignore
            audience=audience,
            issuer=issuer,
            options={"verify_signature": verify},
        )
    except Exception as e:
        raise JWTDecodeError(*e.args) from e
