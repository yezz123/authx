"""Ready to use and customizable Authentications and Oauth2 management for FastAPI and Starlette."""

__version__ = "1.7.1"

from authx._internal._ratelimit import RateLimiter
from authx._internal._session import SessionInfo
from authx.config import AuthXConfig
from authx.dependencies import AuthXDependency
from authx.exceptions import (
    InsufficientScopeError,
    JWTDecodeError,
    LoginTypeMismatchError,
    PolicyDeniedError,
    PolicyEvaluationError,
    RateLimitExceeded,
    TokenExpiredError,
    TokenInvalidAudienceError,
    TokenInvalidIssuerError,
    TokenInvalidSignatureError,
)
from authx.main import AuthX
from authx.manager import AuthManager
from authx.policy import (
    PolicyCondition,
    PolicyContext,
    PolicyDecision,
    PolicyEngine,
    PolicyRule,
)
from authx.schema import RequestToken, TokenPayload, TokenResponse

__all__ = (
    "AuthXConfig",
    "RequestToken",
    "TokenPayload",
    "TokenResponse",
    "AuthX",
    "AuthManager",
    "AuthXDependency",
    "InsufficientScopeError",
    "JWTDecodeError",
    "LoginTypeMismatchError",
    "PolicyDeniedError",
    "PolicyEvaluationError",
    "PolicyCondition",
    "PolicyContext",
    "PolicyDecision",
    "PolicyEngine",
    "PolicyRule",
    "TokenExpiredError",
    "TokenInvalidAudienceError",
    "TokenInvalidIssuerError",
    "TokenInvalidSignatureError",
    "RateLimiter",
    "RateLimitExceeded",
    "SessionInfo",
)
