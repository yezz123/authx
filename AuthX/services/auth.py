import asyncio
from datetime import datetime
from typing import Dict, Optional

from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException
from pydantic.error_wrappers import ValidationError

from AuthX.api import UsersRepo
from AuthX.core.email import EmailClient
from AuthX.core.jwt import JWTBackend
from AuthX.core.logger import logger
from AuthX.core.password import get_password_hash, verify_password
from AuthX.core.user import User
from AuthX.models.user import (
    UserInChangeUsername,
    UserInCreate,
    UserInLogin,
    UserInRegister,
    UserPayload,
)
from AuthX.resources.error_messages import get_error_message
from AuthX.utils.captcha import validate_captcha
from AuthX.utils.strings import create_random_string, hash_string


class AuthService:
    _repo: UsersRepo
    _auth_backend: JWTBackend
    _debug: bool
    _base_url: str
    _site: str
    _recaptcha_secret: str
    _smtp_username: str
    _smtp_password: str
    _smtp_host: str
    _smtp_tls: int
    _display_name: str
    """ POST /logout

    Args:
        access_token: access token.

    Returns:
        None.

    Raises:
        HTTPException:
            401 - invalid access token.
    """

    def __init__(self, user: Optional[User] = None) -> None:
        self._user = user

    @classmethod
    def setup(
        cls,
        repo: UsersRepo,
        auth_backend: JWTBackend,
        debug: bool,
        base_url: str,
        site: str,
        recaptcha_secret: str,
        smtp_username: str,
        smtp_password: str,
        smtp_host: str,
        smtp_tls: int,
        display_name: str,
    ) -> None:
        cls._repo = repo
        cls._auth_backend = auth_backend
        cls._debug = debug
        cls._recaptcha_secret = recaptcha_secret
        cls._smtp_username = smtp_username
        cls._smtp_password = smtp_password
        cls._smtp_host = smtp_host
        cls._smtp_tls = smtp_tls
        cls._base_url = base_url
        cls._site = site
        cls._display_name = display_name

    def _validate_user_model(self, model, data: dict):
        try:
            return model(**data)
        except ValidationError as e:
            msg = e.errors()[0].get("msg")
            raise HTTPException(400, detail=get_error_message(msg))

    async def _email_exists(self, email: str) -> bool:
        return await self._repo.get_by_email(email) is not None

    async def _username_exists(self, username: str) -> bool:
        return await self._repo.get_by_username(username) is not None

    def _create_email_client(self) -> EmailClient:
        return EmailClient(
            self._smtp_username,
            self._smtp_host,
            self._smtp_password,
            self._smtp_tls,
            self._base_url,
            self._site,
            self._display_name,
        )

    async def _request_email_confirmation(self, email: str) -> None:
        token = create_random_string()
        token_hash = hash_string(token)
        await self._repo.request_email_confirmation(email, token_hash)
        email_client = self._create_email_client()
        await email_client.send_confirmation_email(email, token)

    async def register(self, data: dict) -> Dict[str, str]:
        """POST /register

        Args:
            data: email, username, password1, password2.

        Returns:
            Access and refresh tokens.

        Raises:
            HTTPException:
                400 - validation error.

        """
        if not self._debug:
            captcha = data.get("captcha")
            if not await validate_captcha(captcha, self._recaptcha_secret):
                raise HTTPException(400, detail=get_error_message("captcha"))

        user = self._validate_user_model(UserInRegister, data)

        if await self._email_exists(user.email):
            raise HTTPException(400, detail=get_error_message("existing email"))

        if await self._username_exists(user.username):
            raise HTTPException(400, detail=get_error_message("existing username"))

        new_user = UserInCreate(
            **user.dict(), password=get_password_hash(user.password1)
        ).dict()

        try:
            validate_email(new_user.get("email"), timeout=5)
        except EmailNotValidError:
            raise HTTPException(400, detail=get_error_message("try another email"))

        new_user_id = await self._repo.create(new_user)

        asyncio.create_task(self._request_email_confirmation(new_user.get("email")))

        payload = UserPayload(id=new_user_id, username=user.username).dict()
        return self._auth_backend.create_tokens(payload)

    async def _is_bruteforce(self, ip: str, login: str) -> bool:
        return await self._repo.is_bruteforce(ip, login)

    async def _update_last_login(self, id: int) -> None:
        await self._repo.update(id, {"last_login": datetime.utcnow()})

    async def login(self, data: dict, ip: str) -> Dict[str, str]:
        """POST /login

        Args:
            data: login, password.
            ip: for bruteforce check.

        Returns:
            Access and refresh tokens.

        Raises:
            HTTPException:
                400 - validation error or ban.
                404 - user doesn't exist.
                429 - bruteforce attempt.
        """
        try:
            user = UserInLogin(**data)
        except ValidationError:
            raise HTTPException(400)

        if await self._is_bruteforce(ip, user.login):
            raise HTTPException(429, detail="Too many requests")

        item = await self._repo.get_by_login(user.login)

        if item is None:
            raise HTTPException(404)

        if not item.get("active"):
            raise HTTPException(400, detail=get_error_message("ban"))

        if not verify_password(user.password, item.get("password")):
            raise HTTPException(401)

        await self._update_last_login(item.get("id"))

        payload = UserPayload(**item).dict()
        return self._auth_backend.create_tokens(payload)

    # async def token(self) -> dict:

    async def refresh_access_token(self, refresh_token: str) -> str:
        """POST /token/refresh

        Args:
            refresh_token: refresh_token from cookies.

        Returns:
            Access token.

        Raises:
            HTTPException:
                401 - type != refresh or ban.
                500 - ttt
        """
        refresh_token_payload = await self._auth_backend.decode_token(refresh_token)
        if (
            refresh_token_payload is None
            or refresh_token_payload.get("type") != "refresh"
        ):
            raise HTTPException(401)

        item = await self._repo.get(refresh_token_payload.get("id"))
        if item is None or not item.get("active"):
            raise HTTPException(401)

        payload = UserPayload(**item).dict()
        return self._auth_backend.create_access_token(payload)

    async def get_email_confirmation_status(self) -> dict:
        """GET /confirm

        Returns:
            Email as str and status as bool in a dict.
            Example: {"email": sample@sample.com, "confirmed": True}
        """
        item = await self._repo.get(self._user.id)

        return {"email": item.get("email"), "confirmed": item.get("confirmed")}

    async def request_email_confirmation(self) -> None:
        """POST /confirm

        If there is no timeout, send email.

        Returns:
            None

        Raises:
            HTTPException:
                400 - confirmed is already True.
                429 - timeout.
        """
        item = await self._repo.get(self._user.id)
        if item.get("confirmed"):
            raise HTTPException(400)

        if not await self._repo.is_email_confirmation_available(self._user.id):
            raise HTTPException(429)

        email = item.get("email")
        await self._request_email_confirmation(email)

        return None

    async def confirm_email(self, token: str) -> None:
        """POST /confirm/{token}

        Hashes token, looks up hash in db, updates "confirmed" to True for email in a row.

        Returns:
            None

        Raises:
            HTTPException:
                403 - no hash in db.
        """
        token_hash = hash_string(token)
        if not await self._repo.confirm_email(token_hash):
            raise HTTPException(403)  # TODO: ??? 400 maybe, change frontend too

        return None

    async def change_username(self, id: int, username: str) -> None:
        """
        Change username, is a function of user id and username.

        Args:
            id (int): user id.
            username (str): new username.

        Raises:
            HTTPException: 400 - username already exists.
            HTTPException: 404 - user not found.

        Returns:
            None
        """
        new_username = self._validate_user_model(
            UserInChangeUsername, {"username": username}
        ).username

        item = await self._repo.get(id)
        old_username = item.get("username")
        if old_username == new_username:
            raise HTTPException(400, detail=get_error_message("username change same"))

        existing_user = await self._repo.get_by_username(new_username)

        if existing_user is not None:
            raise HTTPException(400, detail=get_error_message("existing username"))

        logger.info(
            f"change_username id={id} old_username={old_username} new_username={new_username}"
        )
        await self._repo.change_username(id, new_username)
        logger.info(f"change_username id={id} success")
        return None
