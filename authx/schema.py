"""This module contains the schema definitions for the AuthX library."""

import datetime
from collections.abc import Sequence
from hmac import compare_digest
from typing import (
    Any,
    Optional,
    Union,
)

from pydantic import BaseModel, Field, ValidationError
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

if PYDANTIC_V2 := PYDANTIC_VERSION.startswith("2."):
    from pydantic import ConfigDict, field_validator  # pragma: no cover
else:
    from pydantic import Extra, validator  # pragma: no cover


class TokenPayload(BaseModel):
    """A comprehensive Pydantic model for managing JSON Web Token (JWT) payloads with advanced token lifecycle handling.

    Provides robust functionality for creating, validating, and manipulating authentication tokens with flexible configuration and extensive metadata support.

    Attributes:
        jti: Unique token identifier.
        iss: Token issuer.
        sub: Subject (user) identifier.
        aud: Token audience.
        exp: Token expiration time.
        nbf: Token not-before time.
        iat: Token issued-at time.
        type: Token type (access or refresh).
        csrf: Cross-Site Request Forgery token.
        scopes: List of token scopes.
        fresh: Flag indicating if the token is freshly issued.

    Methods:
        issued_at: Converts issued time to datetime.
        expiry_datetime: Calculates token expiration datetime.
        time_until_expiry: Calculates remaining time before token expiration.
        time_since_issued: Calculates time elapsed since token issuance.
        has_scopes: Checks if token has specific scopes.
        encode: Creates a JWT token.
        decode: Decodes and validates a JWT token.
    """

    if PYDANTIC_V2:
        model_config = ConfigDict(extra="allow", from_attributes=True)  # pragma: no cover
    else:

        class Config:  # pragma: no cover
            """Configuration class for Pydantic model with extra field handling.

            Allows additional fields beyond the defined model schema to be included during model creation.
            """

            extra = Extra.allow  # pragma: no cover

    jti: Optional[str] = Field(default_factory=get_uuid)
    iss: Optional[str] = None
    sub: str
    aud: Optional[StringOrSequence] = None
    exp: Optional[DateTimeExpression] = None
    nbf: Optional[Union[Numeric, DateTimeExpression]] = None
    iat: Optional[Union[Numeric, DateTimeExpression]] = Field(default_factory=lambda: int(get_now_ts()))
    type: Optional[str] = Field(
        default="access",
        description="Token type",
    )
    csrf: Optional[str] = ""
    scopes: Optional[list[str]] = None
    fresh: bool = False

    @property
    def _additional_fields(self) -> set[str]:
        if PYDANTIC_V2:
            return set(self.__dict__) - set(self.model_fields)  # pragma: no cover
        else:
            return set(self.__dict__) - set(self.__fields__)  # pragma: no cover

    @property
    def extra_dict(self) -> dict[str, Any]:
        """Retrieve additional fields not defined in the base Pydantic model schema.

        Provides a dictionary of extra fields with version-specific compatibility for Pydantic v1 and v2.

        Returns:
            A dictionary containing additional fields beyond the model's defined schema.
        """
        if PYDANTIC_V2:
            return self.model_dump(include=self._additional_fields)  # pragma: no cover
        else:
            return self.dict(include=self._additional_fields)  # pragma: no cover

    @property
    def issued_at(self) -> datetime.datetime:
        """Convert the token's issued-at timestamp to a datetime object.

        Transforms the issued-at (iat) claim into a standardized UTC datetime representation.

        Returns:
            A datetime object representing the token's issuance time.

        Raises:
            TypeError: If the issued-at claim is not a float, int, or datetime object.
        """
        if isinstance(self.iat, (float, int)):
            return datetime.datetime.fromtimestamp(self.iat, tz=datetime.timezone.utc)
        elif isinstance(self.iat, datetime.datetime):
            return self.iat
        else:
            raise TypeError("'iat' claim should be of type float | int | datetime.datetime")

    @property
    def expiry_datetime(self) -> datetime.datetime:
        """Convert the token's expiration claim to a precise datetime object.

        Transforms the expiration (exp) claim into a standardized UTC datetime representation, supporting multiple input types.

        Returns:
            A datetime object representing the token's expiration time.

        Raises:
            TypeError: If the expiration claim is not a float, int, datetime, or timedelta object.
        """
        if isinstance(self.exp, datetime.datetime):  # pragma: no cover
            return self.exp  # pragma: no cover
        elif isinstance(self.exp, datetime.timedelta):
            return self.issued_at + self.exp
        elif isinstance(self.exp, (float, int)):
            return datetime.datetime.fromtimestamp(self.exp, tz=datetime.timezone.utc)  # pragma: no cover
        else:
            raise TypeError("'exp' claim should be of type float | int | datetime.datetime")

    @property
    def time_until_expiry(self) -> datetime.timedelta:
        """Calculate the remaining time before the token expires.

        Computes the time difference between the token's expiration datetime and the current time.

        Returns:
            A timedelta object representing the remaining time until token expiration.
        """
        return self.expiry_datetime - get_now()

    @property
    def time_since_issued(self) -> datetime.timedelta:
        """Calculate the elapsed time since the token was issued.

        Computes the time difference between the current time and the token's issued datetime.

        Returns:
            A timedelta object representing the time elapsed since token issuance.
        """
        return get_now() - self.issued_at

    if PYDANTIC_V2:

        @field_validator("exp", "nbf", mode="before")  # pragma: no cover
        def _set_default_ts(
            cls, value: Union[float, int, datetime.datetime, datetime.timedelta]
        ) -> Union[float, int]:  # pragma: no cover
            if isinstance(value, datetime.datetime):
                return value.timestamp()
            elif isinstance(value, datetime.timedelta):
                return (get_now() + value).timestamp()
            return value
    else:

        @validator("exp", "nbf", pre=True)  # pragma: no cover
        def _set_default_ts(
            cls, value: Union[float, int, datetime.datetime, datetime.timedelta]
        ) -> Union[float, int]:  # pragma: no cover
            if isinstance(value, datetime.datetime):
                return value.timestamp()
            elif isinstance(value, datetime.timedelta):
                return (get_now() + value).timestamp()
            return value

    def has_scopes(self, *scopes: Sequence[str]) -> bool:
        """Check if the token contains all specified scopes.

        Verifies whether the token's scopes include all the requested scope values.

        Args:
            *scopes: Variable number of scope strings to check against the token's scopes.

        Returns:
            A boolean indicating whether all specified scopes are present in the token.
        """
        # if `self.scopes`` is None, the function will immediately return False.
        # If `self.scopes`` is not None, it will check if all elements in scopes are in `self.scopes``.
        return all(s in self.scopes for s in scopes) if self.scopes is not None else False

    def encode(
        self,
        key: str,
        algorithm: AlgorithmType = "HS256",
        ignore_errors: bool = True,
        headers: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> str:
        """Generate a JSON Web Token (JWT) with the current payload's claims and configuration.

        Creates a signed token using the specified cryptographic key and algorithm, incorporating all token metadata.

        Args:
            key: The cryptographic key used for token signing.
            algorithm: The cryptographic algorithm for token signing. Defaults to HS256.
            ignore_errors: Flag to suppress potential encoding errors. Defaults to True.
            headers: Optional custom headers to include in the token.
            data: Optional additional data to embed in the token.

        Returns:
            A string representing the encoded and signed JWT.
        """
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
            data=data,
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
        """Decode and validate a JSON Web Token (JWT) into a TokenPayload instance.

        Converts a signed token into a structured payload object, with optional verification and validation parameters.

        Args:
            token: The encoded JWT string to be decoded.
            key: The cryptographic key used for token verification.
            algorithms: Optional list of allowed cryptographic algorithms. Defaults to HS256.
            audience: Optional expected token audience.
            issuer: Optional expected token issuer.
            verify: Flag to enable or disable token verification. Defaults to True.

        Returns:
            A TokenPayload instance representing the decoded token's claims.
        """
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
        return cls.model_validate(payload) if PYDANTIC_V2 else cls(**payload)


class RequestToken(BaseModel):
    """Verify and validate a token with comprehensive security checks.

    Performs multiple layers of token validation including JWT decoding, type verification, CSRF protection, and freshness checks.

    Args:
        key: The cryptographic key used for token verification.
        algorithms: Optional list of allowed cryptographic algorithms. Defaults to HS256.
        audience: Optional expected token audience.
        issuer: Optional expected token issuer.
        verify_jwt: Flag to enable JWT verification. Defaults to True.
        verify_type: Flag to validate token type matches expected type. Defaults to True.
        verify_csrf: Flag to perform Cross-Site Request Forgery protection. Defaults to True.
        verify_fresh: Flag to require a fresh token. Defaults to False.

    Returns:
        A validated TokenPayload instance representing the decoded token.

    Raises:
        JWTDecodeError: If token decoding fails.
        TokenTypeError: If token type does not match expected type.
        FreshTokenRequiredError: If a fresh token is required but not provided.
        CSRFError: If CSRF token validation fails.
    """

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
        """Verify and validate a token with comprehensive security checks.

        Performs multiple layers of token validation including JWT decoding, type verification, CSRF protection, and freshness checks.

        Args:
            key: The cryptographic key used for token verification.
            algorithms: Optional list of allowed cryptographic algorithms. Defaults to HS256.
            audience: Optional expected token audience.
            issuer: Optional expected token issuer.
            verify_jwt: Flag to enable JWT verification. Defaults to True.
            verify_type: Flag to validate token type matches expected type. Defaults to True.
            verify_csrf: Flag to perform Cross-Site Request Forgery protection. Defaults to True.
            verify_fresh: Flag to require a fresh token. Defaults to False.

        Returns:
            A validated TokenPayload instance representing the decoded token.

        Raises:
            JWTDecodeError: If token decoding fails.
            TokenTypeError: If token type does not match expected type.
            FreshTokenRequiredError: If a fresh token is required but not provided.
            CSRFError: If CSRF token validation fails.
        """
        if algorithms is None:  # pragma: no cover
            algorithms = ["HS256"]  # pragma: no cover
        try:
            decoded_token = decode_token(
                token=self.token,
                key=key,
                algorithms=algorithms,
                verify=verify_jwt,
                audience=audience,
                issuer=issuer,
            )
            payload = TokenPayload.model_validate(decoded_token) if PYDANTIC_V2 else TokenPayload(**decoded_token)
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
                raise CSRFError("Cookies token missing CSRF claim")  # pragma: no cover
            if not compare_digest(self.csrf, payload.csrf):
                raise CSRFError("CSRF token mismatch")

        return payload
