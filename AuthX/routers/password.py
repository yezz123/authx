from typing import Callable

from fastapi import APIRouter, Depends, Request

from AuthX.api import UsersRepo
from AuthX.core.jwt import JWTBackend
from AuthX.core.user import User
from AuthX.services import PasswordService


def get_router(
    repo: UsersRepo,
    auth_backend: JWTBackend,
    get_authenticated_user: Callable,
    debug: bool,
    base_url: str,
    site: str,
    recaptcha_secret: str,
    smtp_username: str,
    smtp_password: str,
    smtp_host: str,
    smtp_tls: int,
    display_name: str,
):
    """
    Setup The Password requirements Router
    Args:
        repo (UsersRepo): The Users Repository
        auth_backend (JWTBackend): The JWT Backend
        get_authenticated_user (Callable): The Authenticated User
        debug (bool): The Debug Mode
        base_url (str): The Base URL
        site (str): The Site Name
        recaptcha_secret (str): The Recaptcha Secret
        smtp_username (str): The SMTP Username
        smtp_password (str): The SMTP Password
        smtp_host (str): The SMTP Host
        smtp_tls (int): The SMTP TLS
        display_name (str): The Display Name

    Returns:
        APIRouter: The Password Router
    """
    PasswordService.setup(
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

    router = APIRouter()

    @router.post("/forgot_password", name="auth:forgot_password")
    async def forgot_password(*, request: Request):
        """
        Forgot Password

        Args:
            request (Request): The Request

        Returns:
            dict: The Response
        """
        data = await request.json()
        ip = request.client.host
        service = PasswordService()
        return await service.forgot_password(data, ip)

    @router.get("/password", name="auth:password_status")
    async def password_status(*, user: User = Depends(get_authenticated_user)):
        """
        Password Status

        Args:
            user (User, optional): The Authenticated User. Defaults to None.

        Returns:
            dict: The Response
        """
        service = PasswordService(user)
        return await service.password_status()

    @router.post("/password", name="auth:password_set")
    async def password_set(
        *, request: Request, user: User = Depends(get_authenticated_user)
    ):
        """
        Set Password

        Args:
            request (Request): The Request
            user (User, optional): The Authenticated User. Defaults to None.

        Returns:
            dict: The Response
        """
        data = await request.json()
        service = PasswordService(user)
        return await service.password_set(data)

    @router.post("/password/{token}", name="auth:password_reset")
    async def password_reset(*, token: str, request: Request):
        """
        Reset Password

        Args:
            token (str): The Token
            request (Request): The Request

        Returns:
            dict: The Response
        """
        data = await request.json()
        service = PasswordService()
        return await service.password_reset(data, token)

    @router.put("/password", name="auth:password_change")
    async def password_change(
        *, request: Request, user: User = Depends(get_authenticated_user)
    ):
        """
        Change Password

        Args:
            request (Request): The Request
            user (User, optional): The Authenticated User. Defaults to Depends(get_authenticated_user).

        Returns:
            dict: The Response
        """
        data = await request.json()
        service = PasswordService(user)
        return await service.password_change(data)

    return router
