from fastapi import APIRouter, Depends, FastAPI

from AuthX import Authentication, User

app = FastAPI()
auth = Authentication()
router = APIRouter()


app.include_router(auth.auth_router, prefix="/api/users")
app.include_router(auth.social_router, prefix="/auth")
app.include_router(auth.password_router, prefix="/api/users")
app.include_router(auth.admin_router, prefix="/api/users")
app.include_router(auth.search_router, prefix="/api/users")

# Set MongoDB and Redis Cache
auth.set_cache(cache)  # aioredis client
auth.set_database(database)  # motor client

# Set Anonymous User
@router.get("/anonym")
def anonym_test(user: User = Depends(auth.get_user)):
    pass


# Set Authenticated User
@router.get("/user")
def user_test(user: User = Depends(auth.get_authenticated_user)):
    pass


#
@router.get("/admin", dependencies=[Depends(auth.admin_required)])
def admin_test():
    pass
