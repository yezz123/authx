import sys

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Set  # pragma: no cover
else:
    from typing_extensions import Set  # pragma: no cover

import datetime
from hmac import compare_digest
from typing import Any, Dict, List, Optional, Sequence, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Extra,
    Field,
    ValidationError,
    field_validator,
    validator,
)
from pydantic.version import VERSION as PYDANTIC_VERSION

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
)

PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")


class PydanticVersionSupportBase(BaseModel):
    if PYDANTIC_V2:
        model_config = ConfigDict(extra="allow")

        @property
        def _additional_fields(self) -> Set[str]:
            return set(self.__dict__) - set(self.model_fields)

        @property
        def extra_dict(self) -> Dict[str, Any]:
            return self.model_dump(include=self._additional_fields)

        @field_validator("exp", "nbf", mode="before", check_fields=False)
        def _set_default_ts(
            cls, value: Union[float, int, datetime.datetime, datetime.timedelta]
        ) -> Union[float, int]:
            if isinstance(value, datetime.datetime):
                return value.timestamp()
            elif isinstance(value, datetime.timedelta):
                return (cls.get_now() + value).timestamp()
            return value

    else:

        class Config:
            extra = Extra.allow

        @property
        def _additional_fields(self):
            return set(self.__dict__) - set(self.__fields__)

        @property
        def extra_dict(self):
            return self.dict(include=self._additional_fields)

        @validator("exp", "nbf", pre=True)
        def _set_default_ts(
            cls, value: Union[float, int, datetime.datetime, datetime.timedelta]
        ) -> Union[float, int]:
            if isinstance(value, datetime.datetime):
                return value.timestamp()
            elif isinstance(value, datetime.timedelta):
                return (cls.get_now() + value).timestamp()
            return value


class TokenPayload(PydanticVersionSupportBase):
    jti: Optional[str] = Field(default_factory=get_uuid)
    iss: Optional[str] = None
    sub: str
    aud: Optional[StringOrSequence] = None
    exp: Optional[DateTimeExpression] = None
    nbf: Optional[Union[Numeric, DateTimeExpression]] = None
    iat: Optional[Union[Numeric, DateTimeExpression]] = Field(
        default_factory=lambda: int(get_now_ts())
    )
    type: Optional[str] = Field(
        default="access",
        description="Token type",
    )
    csrf: Optional[str] = ""
    scopes: Optional[List[str]] = None
    fresh: bool = False

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
        if isinstance(self.exp, datetime.datetime):  # pragma: no cover
            return self.exp  # pragma: no cover
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

    def has_scopes(self, *scopes: Sequence[str]) -> bool:
        # if `self.scopes`` is None, the function will immediately return False.
        # If `self.scopes`` is not None, it will check if all elements in scopes are in `self.scopes``.
        return (
            all(s in self.scopes for s in scopes) if self.scopes is not None else False
        )

    def encode(
        self,
        key: str,
        algorithm: AlgorithmType = "HS256",
        ignore_errors: bool = True,
        headers: Optional[Dict[str, Any]] = None,
    ) -> str:
        return create_token(
            key=key,
            algorithm=algorithm,
            uid=str(self.sub),
            jti=self.jti,
            issued=self.iat,
            # TODO: Fix type hinting for `type` Field
            # it's caused because Type is a string & what we expect is a TokenType
            # TokenType = Literal["access", "refresh"]
            # Investigate if it's possible to fix this
            type=self.type,  # type: ignore
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
        algorithms: Optional[Sequence[AlgorithmType]] = None,
        audience: Optional[StringOrSequence] = None,
        issuer: Optional[str] = None,
        verify: bool = True,
    ) -> "TokenPayload":
        if algorithms is None:  # pragma: no cover
            algorithms = ["HS256"]  # pragma: no cover
        payload = decode_token(
            token=token,
            key=key,
            algorithms=algorithms,
            audience=audience,
            issuer=issuer,
            verify=verify,
        )
        return cls.model_validate(payload) if PYDANTIC_V2 else cls.parse_obj(payload)


class RequestToken(BaseModel):
    token: str = Field(..., description="The token to verify")
    csrf: Optional[str] = None
    type: TokenType = "access"
    location: TokenLocation

    def verify(
        self,
        key: str,
        algorithms: Optional[Sequence[AlgorithmType]] = None,
        audience: Optional[StringOrSequence] = None,
        issuer: Optional[str] = None,
        verify_jwt: bool = True,
        verify_type: bool = True,
        verify_csrf: bool = True,
        verify_fresh: bool = False,
    ) -> TokenPayload:
        if algorithms is None:  # pragma: no cover
            algorithms = ["HS256"]  # pragma: no cover
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
            if PYDANTIC_V2:
                payload = TokenPayload.model_validate(decoded_token)
            else:
                payload = TokenPayload.parse_obj(decoded_token)
        except JWTDecodeError as e:
            raise JWTDecodeError(*e.args) from e
        except ValidationError as e:
            raise JWTDecodeError(*e.args) from e

        if verify_type and (self.type != payload.type):
            error_msg = f"'{self.type}' token required, '{payload.type}' token received"
            if self.type == "access":
                raise AccessTokenRequiredError(error_msg)
            elif self.type == "refresh":  # pragma: no cover
                raise RefreshTokenRequiredError(error_msg)  # pragma: no cover
            raise TokenTypeError(error_msg)  # pragma: no cover

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
