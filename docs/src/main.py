from fastapi import APIRouter, Depends, FastAPI

from authx import Authentication, BaseDBBackend, RedisBackend, User

app = FastAPI()
auth = Authentication(database_backend=BaseDBBackend())
router = APIRouter()

# Set up Pre-configured Routes
app.include_router(auth.auth_router, prefix="/api/users")
app.include_router(auth.social_router, prefix="/auth")
app.include_router(auth.password_router, prefix="/api/users")
app.include_router(auth.admin_router, prefix="/api/users")
app.include_router(auth.search_router, prefix="/api/users")

# Set Redis Cache
auth.set_cache(RedisBackend)

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
