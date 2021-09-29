from typing import Callable, Dict

from fastapi import APIRouter, Body, Depends, Request, Response
from fastapi.exceptions import HTTPException

from AuthX.api import UsersRepo
from AuthX.core.jwt import JWTBackend
from AuthX.core.user import User
from AuthX.services import AuthService

"""
POST /register
POST /login
POST /logout
POST /token
POST /token/refresh
GET /confirm
POST /confirm
POST /confirm/{token}
"""


def get_router(
    repo: UsersRepo,
    auth_backend: JWTBackend,
    get_authenticated_user: Callable,
    debug: bool,
    base_url: str,
    site: str,
    access_cookie_name: str,
    refresh_cookie_name: str,
    access_expiration: int,
    refresh_expiration: int,
    recaptcha_secret: str,
    smtp_username: str,
    smtp_password: str,
    smtp_host: str,
    smtp_tls: int,
    display_name: str,
) -> APIRouter:

    AuthService.setup(
        repo,
        auth_backend,
        debug,
        base_url,
        site,
        recaptcha_secret,
        smtp_username,
        smtp_password,
        smtp_host,
        smtp_tls,
        display_name,
    )

    def set_access_token_in_response(response, token: str) -> None:
        response.set_cookie(
            key=access_cookie_name,
            value=token,
            secure=not debug,
            httponly=True,
            max_age=access_expiration,
        )

    def set_refresh_token_in_response(response, token: str) -> None:
        response.set_cookie(
            key=refresh_cookie_name,
            value=token,
            secure=not debug,
            httponly=True,
            max_age=refresh_expiration,
        )

    def set_tokens_in_response(response, tokens: Dict[str, str]) -> None:
        access_token = tokens.get("access")
        refresh_token = tokens.get("refresh")
        set_access_token_in_response(response, access_token)
        set_refresh_token_in_response(response, refresh_token)

    router = APIRouter()

    @router.post("/register", name="auth:register")
    async def register(*, request: Request, response: Response):
        """
        register a new user
        Args:
            request: Request
            response: Response

        Returns:
            Response
        """
        data = await request.json()
        service = AuthService()

        tokens = await service.register(data)
        set_tokens_in_response(response, tokens)
        return None

    @router.post("/login", name="auth:login")
    async def login(*, request: Request, response: Response):
        """
        login a user

        Args:
            request (Request): Request
            response (Response): Response

        Returns:
            Response
        """
        data = await request.json()
        service = AuthService()

        ip = request.client.host

        tokens = await service.login(data, ip)
        set_tokens_in_response(response, tokens)
        return None

    @router.post("/logout", name="auth:logout")
    async def logout(*, response: Response):
        """
        logout a user

        Args:
            response (Response): Response

        Returns:
            Response
        """
        response.delete_cookie(access_cookie_name)
        response.delete_cookie(refresh_cookie_name)
        return None

    @router.post("/token", name="auth:token")
    async def token(*, user: User = Depends(get_authenticated_user)):
        """
        get a new token

        Args:
            user (User, optional): User. Defaults to None.

        Returns:
            Response
        """
        return user.data

    @router.post("/token/refresh", name="auth:refresh_access_token")
    async def refresh_access_token(
        *, request: Request, response: Response,
    ):
        """
        refresh an access token

        Args:
            request (Request): Request
            response (Response): Response

        Raises:
            HTTPException: HTTPException

        Returns:
            Response
        """
        service = AuthService()
        refresh_token = request.cookies.get(refresh_cookie_name)
        if refresh_token is None:
            raise HTTPException(401)

        access_token = await service.refresh_access_token(refresh_token)
        set_access_token_in_response(response, access_token)
        return {"access": access_token}

    @router.get("/confirm", name="auth:get_email_confirmation_status")
    async def get_email_confirmation_status(
        *, user: User = Depends(get_authenticated_user)
    ):
        """
        get the email confirmation status of a user

        Args:
            user (User, optional): User. Defaults to Depends(get_authenticated_user).

        Returns:
            Response
        """
        service = AuthService(user)
        return await service.get_email_confirmation_status()

    @router.post("/confirm", name="auth:request_email_confirmation")
    async def request_email_confirmation(
        *, user: User = Depends(get_authenticated_user)
    ):
        """
        request an email confirmation

        Args:
            user (User, optional): User. Defaults to Depends(get_authenticated_user).

        Returns:
            Response
        """
        service = AuthService(user)
        return await service.request_email_confirmation()

    @router.post("/confirm/{token}", name="auth:confirm_email")
    async def confirm_email(*, token: str):
        """
        confirm an email

        Args:
            token (str): token

        Returns:
            Response
        """
        service = AuthService()
        return await service.confirm_email(token)

    @router.post("/{id}/change_username", name="auth:change_username")
    async def change_username(
        *,
        id: int,
        username: str = Body("", embed=True),
        user: User = Depends(get_authenticated_user),
    ):
        """
        change the username of a user

        Args:
            id (int): id
            username (str, optional): username. Defaults to Body("", embed=True).
            user (User, optional): User. Defaults to Depends(get_authenticated_user).

        Raises:
            HTTPException: HTTPException

        Returns:
            Response
        """
        service = AuthService(user)
        if user.id == id or user.is_admin:
            return await service.change_username(id, username)
        else:
            raise HTTPException(403)

    return router
