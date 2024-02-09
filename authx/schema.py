import datetime
from hmac import compare_digest
from typing import Any, Dict, List, Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field, ValidationError, validator

from authx._internal._utils import get_now, get_now_ts, get_uuid
from authx.exceptions import (
    AccessTokenRequiredError,
    CSRFError,
    FreshTokenRequiredError,
    JWTDecodeError,
    RefreshTokenRequiredError,
    TokenTypeError,
)
from authx.token import create_token, decode_token
from authx.types import (
    AlgorithmType,
    DateTimeExpression,
    Numeric,
    StringOrSequence,
    TokenLocation,
    TokenType,
    Union,
)


class TokenPayload(BaseModel):
    model_config = ConfigDict(extra="allow")
    jti: Optional[str] = Field(default_factory=get_uuid)
    iss: Optional[str] = None
    sub: Optional[str] = None
    aud: Optional[str] = None
    exp: Optional[Union[Numeric, DateTimeExpression]] = None
    nbf: Optional[Union[Numeric, DateTimeExpression]] = None
    iat: Optional[Union[Numeric, DateTimeExpression]] = Field(
        default_factory=lambda: int(get_now_ts())
    )
    type: Optional[str] = None
    csrf: Optional[str] = None
    scopes: Optional[List[str]] = None
    fresh: bool = False

    @property
    def _additional_fields(self):
        return set(self.__dict__) - set(self.model_fields)

    @property
    def extra_dict(self):
        return self.model_dump(include=self._additional_fields)

    @property
    def issued_at(self) -> datetime.datetime:
        if isinstance(self.iat, (float, int)):
            return datetime.datetime.fromtimestamp(self.iat, tz=datetime.timezone.utc)
        elif isinstance(self.iat, datetime.datetime):
            return self.iat
        else:
            raise TypeError(
                "'iat' claim should be of type float | int | datetime.datetime"
            )

    @property
    def expiry_datetime(self) -> datetime.datetime:
        if isinstance(self.exp, datetime.datetime):
            return self.exp
        elif isinstance(self.exp, datetime.timedelta):
            return self.issued_at + self.exp
        elif isinstance(self.exp, (float, int)):
            return datetime.datetime.fromtimestamp(self.exp, tz=datetime.timezone.utc)
        else:
            raise TypeError(
                "'exp' claim should be of type float | int | datetime.datetime"
            )

    @property
    def time_until_expiry(self) -> datetime.timedelta:
        return self.expiry_datetime - get_now()

    @property
    def time_since_issued(self) -> datetime.timedelta:
        return get_now() - self.issued_at

    @validator("exp", "nbf", always=True)
    def _set_default_ts(cls, value):
        if isinstance(value, datetime.datetime):
            return value.timestamp()
        elif isinstance(value, datetime.timedelta):
            return (get_now() + value).timestamp()
        return value

    def has_scopes(self, *scopes: Sequence[str]) -> bool:
        return all(s in self.scopes for s in scopes)

    def encode(
        self,
        key: str,
        algorithm: str,
        ignore_errors: bool = True,
        headers: Optional[Dict[str, Any]] = None,
    ) -> str:
        return create_token(
            key=key,
            algorithm=algorithm,
            uid=self.sub,
            jti=self.jti,
            issued=self.iat,
            type=self.type,
            expiry=self.exp,
            fresh=self.fresh,
            csrf=self.csrf,
            audience=self.aud,
            issuer=self.iss,
            not_before=self.nbf,
            ignore_errors=ignore_errors,
            headers=headers,
        )

    @classmethod
    def decode(
        cls,
        token: str,
        key: str,
        algorithms: Sequence[AlgorithmType] = ["HS256"],
        audience: Optional[StringOrSequence] = None,
        issuer: Optional[str] = None,
        verify: bool = True,
    ) -> "TokenPayload":
        payload = decode_token(
            token=token,
            key=key,
            algorithms=algorithms,
            audience=audience,
            issuer=issuer,
            verify=verify,
        )
        return cls.model_validate(payload)


class RequestToken(BaseModel):
    token: Optional[str] = None
    csrf: Optional[str] = None
    type: TokenType = "access"
    location: TokenLocation

    def verify(
        self,
        key: str,
        algorithms: Sequence[AlgorithmType] = ["HS256"],
        audience: Optional[StringOrSequence] = None,
        issuer: Optional[str] = None,
        verify_jwt: bool = True,
        verify_type: bool = True,
        verify_csrf: bool = True,
        verify_fresh: bool = False,
    ) -> TokenPayload:
        # JWT Base Verification
        try:
            decoded_token = decode_token(
                token=self.token,
                key=key,
                algorithms=algorithms,
                verify=verify_jwt,
                audience=audience,
                issuer=issuer,
            )
            # Parse payload
            payload = TokenPayload.parse_obj(decoded_token)
        except JWTDecodeError as e:
            raise JWTDecodeError(*e.args) from e
        except ValidationError as e:
            raise JWTDecodeError(*e.args) from e

        if verify_type and (self.type != payload.type):
            error_msg = f"'{self.type}' token required, '{payload.type}' token received"
            if self.type == "access":
                raise AccessTokenRequiredError(error_msg)
            elif self.type == "refresh":
                raise RefreshTokenRequiredError(error_msg)
            raise TokenTypeError(error_msg)

        if verify_fresh and not payload.fresh:
            raise FreshTokenRequiredError("Fresh token required")

        if verify_csrf and self.location == "cookies":
            if self.csrf is None:
                raise CSRFError(f"Missing CSRF token in {self.location}")
            if payload.csrf is None:
                raise CSRFError("Cookies token missing CSRF claim")
            if not compare_digest(self.csrf, payload.csrf):
                raise CSRFError("CSRF token mismatch")

        return payload
