import hashlib
import os
from typing import Iterable, Optional

from AuthX.api import UsersRepo
from AuthX.core.jwt import JWTBackend
from AuthX.errors.social import SocialException
from AuthX.services import SocialService
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse


def check_state(query: str, session: str) -> bool:
    return query == session


def get_router(
    repo: UsersRepo,
    auth_backend: JWTBackend,
    debug: bool,
    language: str,
    base_url: str,
    access_cookie_name: str,
    refresh_cookie_name: str,
    access_expiration: int,
    refresh_expiration: int,
    social_providers: Iterable[str],
    social_creds: Optional[dict],
):

    SocialService.setup(repo, auth_backend, language, base_url, social_creds)

    router = APIRouter()

    def check_provider(provider):
        if provider not in social_providers:
            raise HTTPException(404)

    @router.get("/{provider}", name="social:login")
    async def login(*, provider: str, request: Request):
        check_provider(provider)
        service = SocialService()
        method = getattr(service, f"login_{provider}")

        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        request.session["state"] = state

        redirect_uri = method(state)
        return RedirectResponse(redirect_uri)

    @router.get("/{provider}/callback", name="social:callback")
    async def callback(*, provider: str, request: Request):
        check_provider(provider)

        state_query = request.query_params.get("state")
        state_session = request.session.get("state")

        if not check_state(state_query, state_session):
            raise HTTPException(403)

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
