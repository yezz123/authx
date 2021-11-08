from authx.routers.admin import get_router as get_admin_router
from authx.routers.auth import get_router as get_auth_router
from authx.routers.password import get_router as get_password_router
from authx.routers.search import get_router as get_search_router
from authx.routers.social import get_router as get_social_router

__all__ = [
    "get_admin_router",
    "get_auth_router",
    "get_password_router",
    "get_search_router",
    "get_social_router",
]
