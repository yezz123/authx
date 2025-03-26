"""Ready to use and customizable Authentications and Oauth2 management for FastAPI and Starlette."""

__version__ = "1.4.2"

from authx.config import AuthXConfig
from authx.dependencies import AuthXDependency
from authx.main import AuthX
from authx.schema import RequestToken, TokenPayload

__all__ = "AuthXConfig", "RequestToken", "TokenPayload", "AuthX", "AuthXDependency"
