from datetime import datetime
from typing import Dict, Optional, Tuple

import jwt
from httpx import AsyncClient

from AuthX.api import UsersRepo
from AuthX.core.jwt import JWTBackend
from AuthX.errors import SocialException
from AuthX.models.social import SocialInCreate
from AuthX.models.user import UserPayload

"""Social Service for authentication and authorization"""


class SocialService:
    _repo: UsersRepo
    _auth_backend: JWTBackend
    _base_url: str
    options: Optional[dict]

    @classmethod
    def setup(
        cls,
        repo: UsersRepo,
        auth_backend: JWTBackend,
        base_url: str,
        options: Optional[dict],
    ) -> None:
        SocialException.setup(base_url)
        cls._repo = repo
        cls._auth_backend = auth_backend
        cls._base_url = base_url
        if options is not None:
            for key, value in options.items():
                setattr(cls, f"{key}_id", value.get("id"))
                setattr(cls, f"{key}_secret", value.get("secret"))

    def _create_redirect_uri(self, provider: str) -> str:
        """
        Create redirect uri for social login

        :param provider: social provider
        :return: redirect uri
        """
        return f"{self._base_url}/auth/{provider}/callback"

    async def _update_last_login(self, id: int) -> None:
        """
        Update last login time

        :param id: user id
        :return: None
        """
        await self._repo.update(id, {"last_login": datetime.utcnow()})

    def login_google(self, state: str) -> str:
        """
        Login with google

        :param state: state
        :return: redirect uri
        """
        redirect_uri = self._create_redirect_uri("google")
        return f"https://accounts.google.com/o/oauth2/v2/auth?scope=email%20profile&response_type=code&state={state}&redirect_uri={redirect_uri}&client_id={self.google_id}"

    async def callback_google(self, code: str) -> Tuple[str, str]:
        redirect_uri = self._create_redirect_uri("google")
        async with AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": self.google_id,
                    "client_secret": self.google_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
        data = response.json()
        id_token = data.get("id_token")
        payload = jwt.decode(id_token, verify=False)
        sid = payload.get("sub")
        email = payload.get("email")

        return sid, email

    def login_facebook(self, state: str) -> str:
        redirect_uri = self._create_redirect_uri("facebook")
        return f"https://www.facebook.com/v8.0/dialog/oauth?client_id={self.facebook_id}&redirect_uri={redirect_uri}&state={state}&scope=email"

    async def callback_facebook(self, code: str) -> Tuple[str, str]:
        redirect_uri = self._create_redirect_uri("facebook")

        async with AsyncClient() as client:
            response = await client.get(
                "https://graph.facebook.com/v8.0/oauth/access_token",
                params={
                    "client_id": self.facebook_id,
                    "redirect_uri": redirect_uri,
                    "client_secret": self.facebook_secret,
                    "code": code,
                },
            )
            access_token = response.json().get("access_token")
            response = await client.get(
                "https://graph.facebook.com/me",
                params={"access_token": access_token, "fields": "id,email"},
            )

        data = response.json()
        sid = data.get("id")
        email = data.get("email")

        return sid, email

    async def resolve_user(self, provider: str, sid: str, email: str) -> Dict[str, str]:
        if email is None:
            raise SocialException(f"email {provider} error", 400)

        existing_user = await self._repo.get_by_social(provider, sid)
        if existing_user is not None:
            await self._repo.update_last_login(existing_user.get("id"))
            item = existing_user
            if not item.get("active"):
                raise SocialException("ban", 401)
        else:
            existing_email = await self._repo.get_by_email(email)
            if existing_email is not None:
                raise SocialException("email exists", 401)

            username = email.split("@")[0]
            i = 0
            resolved_username = username
            postfix = str(i) if i > 0 else ""
            while True:
                resolved_username = f"{username}{postfix}"
                existing_username = await self._repo.get_by_username(resolved_username)
                if not existing_username:
                    break

            user = SocialInCreate(
                **{
                    "email": email,
                    "username": resolved_username,
                    "provider": provider,
                    "sid": sid,
                }
            ).dict()

            user_id = await self._repo.create(user)
            item = user.update({"id": user_id})

        payload = UserPayload(**item).dict()

        return self._auth_backend.create_tokens(payload)
