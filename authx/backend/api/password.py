from typing import Optional

from authx.backend.base import Base
from authx.core.config import (
    PASSWORD_RESET_LIFETIME,
    PASSWORD_RESET_MAX,
    PASSWORD_RESET_TIMEOUT,
)


class UsersPasswordMixin(Base):
    """User Password MIXIN

    Args:
        Create all the Common Password GET, POST, PUT, DELETE methods.
    """

    async def get_password_status(self, id: int) -> str:
        """
        Get the password status of a user.

        Args:
            id (int): The id of the user.

        Returns:
            str: The password status.
        """
        item = await self.get(id)
        if item.get("provider") is not None and item.get("password") is None:
            return "set"  # pragma: no cover
        else:
            return "change"

    async def set_password(self, id: int, password: str) -> None:
        """
        Set the password of a user.

        Args:
            id (int): The id of the user.
            password (str): The password.
        """
        await self.update(id, {"password": password})

    async def is_password_reset_available(self, id: int) -> bool:
        """
        Check if the password reset is available.

        Args:
            id (int): The id of the user.

        Returns:
            bool: True if the password reset is available.
        """
        key = f"users:reset:count:{id}"
        return await self._check_timeout_and_incr(
            key, PASSWORD_RESET_MAX, PASSWORD_RESET_TIMEOUT
        )  # type: ignore

    async def set_password_reset_token(self, id: int, token_hash: str) -> None:
        """
        Set the password reset token of a user.

        Args:
            id (int): The id of the user.
            token_hash (str): The token hash.
        """
        key = f"users:reset:token:{token_hash}"
        await self._cache.set(key, id, expire=PASSWORD_RESET_LIFETIME)

    async def get_id_for_password_reset(self, token_hash: str) -> Optional[int]:
        """
        Get the id for a password reset token.

        Args:
            token_hash (str): The token hash.

        Returns:
            Optional[int]: The id for the token.
        """
        id = await self._cache.get(f"users:reset:token:{token_hash}")
        return int(id) if id is not None else None
