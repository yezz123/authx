"""Exceptions for AuthX."""

from typing import Any, Optional


class AuthXException(Exception):
    """Base AuthXException Exception."""

    def __init__(self, *args: Any, login_type: Optional[str] = None, **kwargs: Any) -> None:
        self.login_type = login_type
        super().__init__(*args)


class BadConfigurationError(AuthXException):
    """Exception raised when AuthX configuration contains wrong parameters."""

    pass


class JWTDecodeError(AuthXException):
    """Exception raised when decoding JSON Web Token fails."""

    pass


class TokenExpiredError(JWTDecodeError):
    """Exception raised when a JSON Web Token has expired."""

    pass


class TokenInvalidSignatureError(JWTDecodeError):
    """Exception raised when a JSON Web Token has an invalid signature."""

    pass


class TokenInvalidAudienceError(JWTDecodeError):
    """Exception raised when a JSON Web Token has an invalid audience."""

    pass


class TokenInvalidIssuerError(JWTDecodeError):
    """Exception raised when a JSON Web Token has an invalid issuer."""

    pass


class NoAuthorizationError(AuthXException):
    """Exception raised when no token can be parsed from request."""

    pass


class CSRFError(AuthXException):
    """Exception raised when CSRF protection failed."""

    pass


class TokenError(AuthXException):
    """Base Exception for token related errors."""

    pass


class MissingTokenError(TokenError):
    """Exception raised when no token can be parsed from request."""

    pass


class MissingCSRFTokenError(MissingTokenError):
    """Exception raised when no CSRF token can be parsed from request."""

    pass


class TokenTypeError(TokenError):
    """Exception raised when a specific token type is expected."""

    pass


class LoginTypeMismatchError(TokenTypeError):
    """Exception raised when a token belongs to a different login type."""

    def __init__(
            self,
            expected_type: str,
            actual_type: Optional[str] = None,
            message: Optional[str] = None,
            login_type: Optional[str] = None,
    ) -> None:
        """Initialize LoginTypeMismatchError.

        Args:
            expected_type: Login type required by the protected endpoint.
            actual_type: Login type found in the token, if it could be determined.
            message: Optional custom error message.
            login_type: The login_type to set on the base exception.
        """
        self.expected_type = expected_type
        self.actual_type = actual_type
        actual = actual_type if actual_type is not None else "unknown"
        if message is None:
            message = f"Token type mismatch: expected '{expected_type}', got '{actual}'"
        super().__init__(message, login_type=login_type)


class RevokedTokenError(TokenError):
    """Exception raised when a revoked token has been used."""

    pass


class TokenRequiredError(TokenError):
    """Exception raised when no token was used in request."""

    pass


class FreshTokenRequiredError(TokenError):
    """Exception raised when a not fresh token was used in request."""

    pass


class AccessTokenRequiredError(TokenTypeError):
    """Exception raised when an `access` token is missing from request."""

    pass


class RefreshTokenRequiredError(TokenTypeError):
    """Exception raised when an `refresh` token is missing from request."""

    pass


class InsufficientScopeError(TokenError):
    """Exception raised when token lacks required scopes.

    Attributes:
        required: List of scopes that were required.
        provided: List of scopes that were provided in the token.
    """

    def __init__(
            self,
            required: list[str],
            provided: Optional[list[str]] = None,
            message: Optional[str] = None,
            login_type: Optional[str] = None,
    ) -> None:
        """Initialize InsufficientScopeError.

        Args:
            required: List of scopes that were required.
            provided: List of scopes that were provided in the token.
            message: Optional custom error message.
            login_type: The login_type to set on the base exception.
        """
        self.required = required
        self.provided = provided or []
        if message is None:
            message = f"Missing required scopes: {required}. Provided: {self.provided}"
        super().__init__(message, login_type=login_type)


class PolicyDeniedError(TokenError):
    """Exception raised when a policy evaluation denies access."""

    def __init__(self, reason: str = "Policy denied access", login_type: Optional[str] = None) -> None:
        """Initialize PolicyDeniedError.

        Args:
            reason: Human-readable reason for the denial.
            login_type: The login_type to set on the base exception.
        """
        self.reason = reason
        super().__init__(reason, login_type=login_type)


class PolicyEvaluationError(AuthXException):
    """Exception raised when a policy evaluator cannot be evaluated."""

    pass


class RateLimitExceeded(AuthXException):
    """Exception raised when a rate limit is exceeded.

    Attributes:
        retry_after: Seconds until the client may retry.
    """

    def __init__(self, retry_after: int = 60, message: Optional[str] = None) -> None:
        """Initialize RateLimitExceeded.

        Args:
            retry_after: Seconds until the client may retry.
            message: Optional custom error message.
        """
        self.retry_after = retry_after
        if message is None:
            message = f"Rate limit exceeded. Retry after {retry_after} seconds."
        super().__init__(message)


class SessionRevoked(AuthXException):
    """Exception raised when an operation uses a revoked session.

    Indicates the session associated with a token has been explicitly revoked.
    """

    pass


class InvalidToken(Exception):
    """When a token is invalid for all identity providers."""

    def __init__(self, errors: str) -> None:
        """Initialize InvalidToken Exception.

        Args:
            errors (list[str]): list of errors
        """
        self.errors = errors


class AuthxArgumentDeprecationWarning(DeprecationWarning):
    """Raised when deprecated argument is used."""

    pass
