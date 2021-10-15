import hashlib
import os
from typing import Iterable, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from AuthX.api import UsersRepo
from AuthX.core.jwt import JWTBackend
from AuthX.errors import SocialException
from AuthX.services import SocialService


def check_state(query: str, session: str) -> bool:
    return query == session


def get_router(
    repo: UsersRepo,
    auth_backend: JWTBackend,
    debug: bool,
    base_url: str,
    access_cookie_name: str,
    refresh_cookie_name: str,
    access_expiration: int,
    refresh_expiration: int,
    social_providers: Iterable[str],
    social_creds: Optional[dict],
):
    """
    Returns a router with all social providers.

    Args:
        repo (UsersRepo): Users repository.
        auth_backend (JWTBackend): JWT backend.
        debug (bool): Debug mode.
        base_url (str): Base URL.
        access_cookie_name (str): Access token cookie name.
        refresh_cookie_name (str): Refresh token cookie name.
        access_expiration (int): Access token expiration.
        refresh_expiration (int): Refresh token expiration.
        social_providers (Iterable[str]): List of social providers.
        social_creds (Optional[dict]): Social credentials.

    Raises:
        HTTPException: If the social provider is not supported.
        HTTPException: If the social provider is not configured.

    Returns:
        APIRouter: Social router.
    """
    SocialService.setup(repo, auth_backend, base_url, social_creds)

    router = APIRouter()

    def check_provider(provider):
        if provider not in social_providers:
            raise HTTPException(404)

    @router.get("/{provider}", name="social:login")
    async def login(*, provider: str, request: Request):
        """
        Redirects to the social provider login page.

        Args:
            provider (str): Social provider.
            request (Request): FastAPI request.

        Returns:
            RedirectResponse: Redirects to the social provider login page.
        """
        check_provider(provider)
        service = SocialService()
        method = getattr(service, f"login_{provider}")

        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        request.session["state"] = state

        redirect_uri = method(state)
        return RedirectResponse(redirect_uri)

    @router.get("/{provider}/callback", name="social:callback")
    async def callback(*, provider: str, request: Request):
        """
        Handles the social provider callback.

        Args:
            provider (str): Social provider.
            request (Request): FastAPI request.

        Raises:
            HTTPException: If the social provider is not supported.

        Returns:
            HTMLResponse: Redirects to the home page.
        """
        check_provider(provider)

        state_query = request.query_params.get("state")
        state_session = request.session.get("state")

        if not check_state(state_query, state_session):
            raise HTTPException(403)
        # TODO: Check if the user is already logged in.
        code = request.query_params.get("code")
        service = SocialService()
        method = getattr(service, f"callback_{provider}")

        sid, email = await method(code)

        try:
            tokens = await service.resolve_user(provider, sid, email)
            response = RedirectResponse("/")
            response.set_cookie(
                key=access_cookie_name,
                value=tokens.get("access"),
                secure=not debug,
                httponly=True,
                max_age=access_expiration,
            )
            response.set_cookie(
                key=refresh_cookie_name,
                value=tokens.get("refresh"),
                secure=not debug,
                httponly=True,
                max_age=refresh_expiration,
            )
            return response
        except SocialException as e:
            return HTMLResponse(e.content, status_code=e.status_code)

    return router
