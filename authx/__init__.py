"""Ready to use and customizable Authentications and Oauth2 management for FastAPI"""

__version__ = "0.3.0"

from authx.api import UsersRepo as UsersRepo
from authx.cache import RedisBackend as RedisBackend
from authx.core import EmailClient as EmailClient
from authx.core import JWTBackend as JWTBackend
from authx.core import User as User
from authx.database import BaseDBBackend as BaseDBBackend
from authx.database import EncodeDBBackend as EncodeDBBackend
from authx.database import MongoDBBackend as MongoDBBackend
from authx.main import Authentication as Authentication
from authx.main import authx as authx
from authx.middleware import MiddlewareOauth2 as MiddlewareOauth2
from authx.routers import get_admin_router as get_admin_router
from authx.routers import get_auth_router as get_auth_router
from authx.routers import get_password_router as get_password_router
from authx.routers import get_search_router as get_search_router
from authx.routers import get_social_router as get_social_router
from authx.services import AdminService as AdminService
from authx.services import AuthService as AuthService
from authx.services import PasswordService as PasswordService
from authx.services import SearchService as SearchService
from authx.services import SocialService as SocialService
