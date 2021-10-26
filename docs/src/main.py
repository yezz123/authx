from fastapi import APIRouter, Depends, FastAPI

from AuthX import Authentication, User
from AuthX.database import MongoDBBackend, RedisBackend

app = FastAPI()
auth = Authentication()
router = APIRouter()

# Set up Pre-configured Routes
app.include_router(auth.auth_router, prefix="/api/users")
app.include_router(auth.social_router, prefix="/auth")
app.include_router(auth.password_router, prefix="/api/users")
app.include_router(auth.admin_router, prefix="/api/users")
app.include_router(auth.search_router, prefix="/api/users")

# Set MongoDB and Redis Cache
auth.set_cache(RedisBackend)  # aioredis client
auth.set_database(MongoDBBackend)  # motor client

# Set Anonymous User
@router.get("/anonym")
def anonym_test(user: User = Depends(auth.get_user)):
    pass


# Set Authenticated User
@router.get("/user")
def user_test(user: User = Depends(auth.get_authenticated_user)):
    pass


# Set Admin User
@router.get("/admin", dependencies=[Depends(auth.admin_required)])
def admin_test():
    pass
