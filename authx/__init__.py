"""Ready to use and customizable Authentications and Oauth2 management for FastAPI"""

__version__ = "0.1.4"

__license__ = "MIT"

__author__ = "Yasser Tahiri"

__author_email__ = "yasserth19@gmail.com"

from authx.main import Authentication, User, authx
from authx.middleware import MiddlewareOauth2

__all__ = ["authx", "Authentication", "User", "MiddlewareOauth2"]
