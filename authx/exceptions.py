"""Exceptions for AuthX."""


class AuthXException(Exception):
    """Base AuthXException Exception."""

    pass


class BadConfigurationError(AuthXException):
    """Exception raised when AuthX configuration contains wrong parameters."""

    pass


class JWTDecodeError(AuthXException):
    """Exception raised when decoding JSON Web Token fails."""

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
