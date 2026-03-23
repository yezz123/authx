"""Ready to use and customizable Authentications and Oauth2 management for FastAPI and Starlette."""

__version__ = "1.5.2"

from authx._internal._ratelimit import RateLimiter
from authx._internal._session import SessionInfo
from authx.config import AuthXConfig
from authx.dependencies import AuthXDependency
from authx.exceptions import InsufficientScopeError, RateLimitExceeded
from authx.main import AuthX
from authx.schema import RequestToken, TokenPayload, TokenResponse

__all__ = (
    "AuthXConfig",
    "RequestToken",
    "TokenPayload",
    "TokenResponse",
    "AuthX",
    "AuthXDependency",
    "InsufficientScopeError",
    "RateLimiter",
    "RateLimitExceeded",
    "SessionInfo",
)
