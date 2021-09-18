from AuthX.routers.admin import get_router as get_admin_router
from AuthX.routers.auth import get_router as get_auth_router
from AuthX.routers.password import get_router as get_password_router
from AuthX.routers.search import get_router as get_search_router
from AuthX.routers.social import get_router as get_social_router

__all__ = [
    "get_admin_router",
    "get_auth_router",
    "get_password_router",
    "get_search_router",
    "get_social_router",
]
