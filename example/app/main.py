import motor.motor_asyncio
from db import db
from decouple import config
from fastapi import APIRouter, Depends, FastAPI

from authx import Authentication, User
from authx.database import MongoDBBackend, RedisBackend

app = FastAPI(
    title="AuthX",
    description="AuthX is a simple authentication system for fastapi.",
    version="0.1.0",
)

auth = Authentication(
    debug=config("DEBUG", default=False, cast=bool),
    base_url=config("BASE_URL", default="http://localhost:8000"),
    site=config("SITE", default="authx"),
    database_name=db,
    callbacks=[],
    access_cookie_name=config("ACCESS_COOKIE_NAME", default="access_token"),
    refresh_cookie_name=config("REFRESH_COOKIE_NAME", default="refresh_token"),
    private_key=config("PRIVATE_KEY", default="private_key"),
    public_key=config("PUBLIC_KEY", default="public_key"),
    access_expiration=config("ACCESS_EXPIRATION", default=3600),
    refresh_expiration=config("REFRESH_EXPIRATION", default=86400),
    smtp_username=config("SMTP_USERNAME", default="username"),
    smtp_password=config("SMTP_PASSWORD", default="password"),
    smtp_host=config("SMTP_HOST", default="smtp.gmail.com"),
    smtp_tls=config("SMTP_TLS", default=True),
    display_name=config("DISPLAY_NAME", default="AuthX"),
    recaptcha_secret=config("RECAPTCHA_SECRET", default="secret"),
    social_providers=[],
    social_creds=None,
)

router = APIRouter()


app.include_router(auth.auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(auth.password_router, prefix="/api/password", tags=["password"])
app.include_router(auth.admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(auth.search_router, prefix="/api/search", tags=["search"])

# TODO: Fix {TypeError: 'MongoDBBackend' object is not subscriptable}
# https://stackoverflow.com/questions/54805511/typeerror-mongoengine-object-is-not-subscriptable
# https://docs.python.org/3/library/typing.html#type-aliases
# https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#creating-a-client

# Set MongoDB and Redis Cache
auth.set_cache(RedisBackend())  # aioredis client
auth.set_database(MongoDBBackend(database_name=db))  # motor client

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
