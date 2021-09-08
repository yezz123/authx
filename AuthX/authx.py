from typing import Iterable, Optional

from aioredis import Redis
from fastapi import APIRouter, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient

from AuthX.api.users import UsersRepo
from AuthX.core.jwt import JWTBackend
from AuthX.core.user import User
from AuthX.database.mongodb import MongoDBBackend
from AuthX.database.redis import RedisBackend
from AuthX.routers.admin import get_router as get_admin_router
from AuthX.routers.auth import get_router as get_auth_router
from AuthX.routers.password import get_router as get_password_router
from AuthX.routers.search import get_router as get_search_router
from AuthX.routers.social import get_router as get_social_router


class Auth:
    def __init__(
        self,
        access_cookie_name: str,
        refresh_cookie_name: str,
        access_expiration: int,
        refresh_expiration: int,
    ) -> None:
        self._access_cookie_name = access_cookie_name
        self._refresh_cookie_name = refresh_cookie_name

        self._cache_backend = RedisBackend()
        self._auth_backend = JWTBackend(
            self._cache_backend, None, access_expiration, refresh_expiration,
        )

    def set_cache(self, client: Redis) -> None:
        self._cache_backend.set_client(client)

    async def get_user(self, request: Request) -> User:
        access_token = request.cookies.get(self._access_cookie_name)
        if access_token:
            return await User.create(access_token, self._auth_backend)
        else:
            return User()

    async def get_authenticated_user(self, request: Request,) -> User:
        access_token = request.cookies.get(self._access_cookie_name)
        if access_token:
            return await User.create(access_token, self._auth_backend)
        else:
            raise HTTPException(401)

    async def admin_required(self, request: Request) -> None:
        access_token = request.cookies.get(self._access_cookie_name)
        if access_token:
            user = await User.create(access_token, self._auth_backend)
            if user.is_admin:
                return

        raise HTTPException(403)


class AuthApp(Auth):
    def __init__(
        self,
        debug: bool,
        language: str,
        base_url: str,
        site: str,
        database_name: str,
        callbacks: Iterable,
        access_cookie_name: str,
        refresh_cookie_name: str,
        access_expiration: int,
        refresh_expiration: int,
        smtp_username: str,
        smtp_password: str,
        smtp_host: str,
        smtp_tls: int,
        display_name: str,
        recaptcha_secret: str,
        social_providers: Iterable,
        social_creds: Optional[dict],
    ) -> None:
        self._debug = debug
        self._language = language
        self._base_url = base_url
        self._site = site
        self._database_name = database_name
        self._access_cookie_name = access_cookie_name
        self._refresh_cookie_name = refresh_cookie_name
        self._access_expiration = access_expiration
        self._refresh_expiration = refresh_expiration
        self._smtp_username = smtp_username
        self._smtp_password = smtp_password
        self._smtp_host = smtp_host
        self._smtp_tls = smtp_tls
        self._display_name = display_name
        self._recaptcha_secret = recaptcha_secret
        self._social_providers = social_providers
        self._social_creds = social_creds

        self._database_backend = MongoDBBackend(self._database_name)
        self._cache_backend = RedisBackend()

        self._auth_backend = JWTBackend(
            self._cache_backend, access_expiration, refresh_expiration,
        )

        self._users_repo = UsersRepo(
            self._database_backend, self._cache_backend, callbacks, access_expiration
        )

    @property
    def auth_router(self) -> APIRouter:
        return get_auth_router(
            self._users_repo,
            self._auth_backend,
            self.get_authenticated_user,
            self._debug,
            self._language,
            self._base_url,
            self._site,
            self._access_cookie_name,
            self._refresh_cookie_name,
            self._access_expiration,
            self._refresh_expiration,
            self._recaptcha_secret,
            self._smtp_username,
            self._smtp_password,
            self._smtp_host,
            self._smtp_tls,
            self._display_name,
        )

    @property
    def password_router(self) -> APIRouter:
        return get_password_router(
            self._users_repo,
            self._auth_backend,
            self.get_authenticated_user,
            self._debug,
            self._language,
            self._base_url,
            self._site,
            self._recaptcha_secret,
            self._smtp_username,
            self._smtp_password,
            self._smtp_host,
            self._smtp_tls,
            self._display_name,
        )

    @property
    def social_router(self) -> APIRouter:
        return get_social_router(
            self._users_repo,
            self._auth_backend,
            self._debug,
            self._language,
            self._base_url,
            self._access_cookie_name,
            self._refresh_cookie_name,
            self._access_expiration,
            self._refresh_expiration,
            self._social_providers,
            self._social_creds,
        )

    @property
    def admin_router(self) -> APIRouter:
        return get_admin_router(self._users_repo, self.admin_required)

    @property
    def search_router(self) -> APIRouter:
        return get_search_router(self._users_repo, self.admin_required)

    def set_database(self, database_client: AsyncIOMotorClient) -> None:
        self._database_backend.set_client(database_client)

    def set_cache(self, cache_client: Redis) -> None:
        self._cache_backend.set_client(cache_client)
