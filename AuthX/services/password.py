from typing import Optional

from fastapi import HTTPException
from pydantic import ValidationError

from AuthX.api import UsersRepo
from AuthX.core.email import EmailClient
from AuthX.core.jwt import JWTBackend
from AuthX.core.logger import logger
from AuthX.core.password import get_password_hash, verify_password
from AuthX.core.user import User
from AuthX.models.user import (
    UserInChangePassword,
    UserInForgotPassword,
    UserInSetPassword,
)
from AuthX.resources.error_messages import get_error_message
from AuthX.utils.strings import create_random_string, hash_string


class PasswordService:
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

    def __init__(self, user: Optional[User] = None) -> None:
        self._user = user

    @classmethod
    def setup(
        cls,
        repo,
        auth_backend,
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

    def _validate_user_model(self, model, data):
        try:
            return model(**data)
        except ValidationError as e:
            msg = e.errors()[0].get("msg")
            raise HTTPException(400, detail=get_error_message(msg))

    async def forgot_password(self, data: dict, ip: str) -> None:
        """POST /forgot_password

        Only for accounts with password.

        Args:
            data: {email: "email@email.com"}
            ip: ip from request

        Returns:
            None

        Raises:
            HTTPException:
                400 - validation or timeout.
                404 - email not found.
        """
        try:
            email = UserInForgotPassword(**data).email
        except ValidationError:
            raise HTTPException(400, detail=get_error_message("validation"))

        item = await self._repo.get_by_email(email)

        if item is None:
            raise HTTPException(404, detail=get_error_message("email not found"))

        if item.get("password") is None:
            raise HTTPException(406)

        id = item.get("id")

        if not await self._repo.is_password_reset_available(id):
            raise HTTPException(400, detail=get_error_message("reset before"))
        logger.info(f"forgot_password ip={ip} email={email}")

        token = create_random_string()
        token_hash = hash_string(token)

        await self._repo.set_password_reset_token(id, token_hash)

        # if not self._debug:  # TODO
        email_client = self._create_email_client()
        await email_client.send_forgot_password_email(email, token)

        return None

    """post /password_status
        Only for accounts with password.

        Returns:
            {
                "password": "",
                "provider": "",
                "reset_available": True,
            }

        Raises:
            HTTPException:
                400 - validation or timeout.
                404 - token not found.
"""

    async def password_status(self) -> dict:
        status = await self._repo.get_password_status(self._user.id)
        return {"status": status}

    async def password_set(self, data: dict) -> None:
        """
        POST /password_set
        Only for accounts with password.

        Args:
            data (dict): {password1: "password", password2: "password"}

        Returns:
            None
        """
        item = await self._repo.get(self._user.id)
        return {
            "password": item.get("password") is not None,
            "provider": item.get("provider") is not None,
            "reset_available": await self._repo.is_password_reset_available(
                self._user.id
            ),
        }

    async def password_set(self, data: dict) -> None:
        """POST /password_set
        Only for accounts with password.

        Args:
            data: {password1: "password", password2: "password"}

        Returns:
            None

        Raises:
            HTTPException:
                400 - validation or timeout.
                404 - token not found.
        """
        item = await self._repo.get(self._user.id)
        if item.get("provider") is not None and item.get("password") is None:
            user_model = self._validate_user_model(UserInSetPassword, data)
            password_hash = get_password_hash(user_model.password1)
            await self._repo.set_password(self._user.id, password_hash)
            return None
        else:
            raise HTTPException(400, get_error_message("password already exists"))

    async def password_reset(self, data: dict, token: str) -> None:
        """POST /password_reset
        Only for accounts with password.

        Args:
            data: {password1: "password", password2: "password"}
            token: token from email

        Returns:
            None

        Raises:
            HTTPException:
                400 - validation or timeout.
                404 - token not found.
        """
        token_hash = hash_string(token)

        id = await self._repo.get_id_for_password_reset(token_hash)
        if id is None:
            raise HTTPException(404)

        user_model = self._validate_user_model(UserInSetPassword, data)

        password_hash = get_password_hash(user_model.password1)
        await self._repo.set_password(id, password_hash)

        return None

    async def password_change(self, data: dict) -> None:
        """POST /password_change
        Only for accounts with password.

        Args:
            data: {password1: "password", password2: "password"}

        Returns:
            None

        Raises:
            HTTPException:
                400 - validation or timeout.
                404 - token not found.
        """
        user_model = self._validate_user_model(UserInChangePassword, data)
        item = await self._repo.get(self._user.id)

        if not verify_password(user_model.old_password, item.get("password")):
            raise HTTPException(400, detail=get_error_message("password invalid"))

        password_hash = get_password_hash(user_model.password1)
        await self._repo.set_password(self._user.id, password_hash)
        return None
