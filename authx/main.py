from typing import Iterable, Optional

from aioredis import Redis
from fastapi import APIRouter, HTTPException, Request

from authx.api import UsersRepo
from authx.cache import RedisBackend
from authx.core.jwt import JWTBackend
from authx.core.user import User
from authx.database import BaseDBBackend
from authx.routers import (
    get_admin_router,
    get_auth_router,
    get_password_router,
    get_search_router,
    get_social_router,
)


class authx:
    """Authx is a fastapi application that provides a simple way to authenticate users.
    Using this application, you can easily create a user management system that allows users to register,
    login, and logout, and also allows admins to manage users.
    """

    def __init__(
        self,
        access_cookie_name: str,
        refresh_cookie_name: str,
        public_key: bytes,
        access_expiration: int,
        refresh_expiration: int,
    ) -> None:
        self._access_cookie_name = access_cookie_name
        self._refresh_cookie_name = refresh_cookie_name

        self._cache_backend = RedisBackend()
        self._auth_backend = JWTBackend(
            self._cache_backend,
            None,
            public_key,
            access_expiration,
            refresh_expiration,
        )

    def set_cache(self, client: Redis) -> None:
        self._cache_backend.set_client(client)

    async def get_user(self, request: Request) -> User:
        if access_token := request.cookies.get(self._access_cookie_name):
            return await User.create(access_token, self._auth_backend)
        else:
            return User()

    async def get_authenticated_user(
        self,
        request: Request,
    ) -> User:
        if access_token := request.cookies.get(self._access_cookie_name):
            return await User.create(access_token, self._auth_backend)
        else:
            raise HTTPException(401)

    async def admin_required(self, request: Request) -> None:
        if access_token := request.cookies.get(self._access_cookie_name):
            user = await User.create(access_token, self._auth_backend)
            if user.is_admin:
                return

        raise HTTPException(403)


class Authentication(authx):
    """Authentication is the Class that handles all the authentication routes, such as login, register,
    and logout, and Support all AuthX Features such as Social Authentication, Password Reset, and Admin,
    and also provides a simple way to create a user management system.
    You Can Add Also the Support to other Authentication Providers such as Google, Facebook.
    Supporting Cache, JWT, and MongoDB.
    """

    def __init__(
        self,
        debug: bool,
        base_url: str,
        site: str,
        database_backend: BaseDBBackend,
        callbacks: Iterable,
        access_cookie_name: str,
        refresh_cookie_name: str,
        private_key: bytes,
        public_key: bytes,
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
        self._base_url = base_url
        self._site = site
        self._access_cookie_name = access_cookie_name
        self._refresh_cookie_name = refresh_cookie_name
        self._private_key = private_key
        self._public_key = public_key
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

        self._database_backend = database_backend
        self._cache_backend = RedisBackend()

        self._auth_backend = JWTBackend(
            self._cache_backend,
            private_key,
            public_key,
            access_expiration,
            refresh_expiration,
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

    def set_cache(self, cache_client: Redis) -> None:
        self._cache_backend.set_client(cache_client)
