import re
from datetime import datetime
from typing import Optional, Tuple

from email_validator import EmailNotValidError, validate_email

from authx.backend.base import Base


class UsersCRUDMixin(Base):
    """User CRUD MIXIN"""

    async def get(self, id: int) -> Optional[dict]:
        """
        Get a user by id.
        """
        return await self._database.get(id)

    async def get_by_email(self, email: str) -> Optional[dict]:
        """
        Get a user by email.
        """
        return await self._database.get_by_email(email)

    async def get_by_username(self, username: str) -> Optional[dict]:
        """
        Get a user by username.
        """
        return await self._database.get_by_username(username)

    async def get_by_social(self, provider: str, sid: str) -> Optional[dict]:
        """
        Get a user by social id.
        """
        return await self._database.get_by_social(provider, sid)  # pragma: no cover

    async def get_by_login(self, login: str) -> Optional[dict]:
        """
        Get a user by login.
        """
        try:
            valid_email = validate_email(login).email
            return await self.get_by_email(valid_email)
        except EmailNotValidError:
            return await self.get_by_username(login)

    async def create(self, obj: dict) -> int:
        """
        Create a user.
        """
        return await self._database.create(obj)  # pragma: no cover

    async def update(self, id: int, obj: dict) -> None:
        """
        Update a user.
        """
        await self._database.update(id, obj)
        return None

    async def delete(self, id: int) -> None:
        """
        Delete a user.
        """
        await self._database.delete(id)  # pragma: no cover
        return None  # pragma: no cover

    async def update_last_login(self, id: int) -> None:
        """
        Update the last login of a user.
        """
        await self.update(id, {"last_login": datetime.utcnow()})  # pragma: no cover

    async def search(
        self, id: int, username: str, p: int, size: int
    ) -> Tuple[dict, int]:
        """
        Search for users.
        """
        if id is not None:  # pragma: no cover
            f = {"id": id}  # pragma: no cover
        elif username is not None and username.strip() != "":  # pragma: no cover
            f = {"username": re.compile(username, re.IGNORECASE)}  # pragma: no cover
        else:  # pragma: no cover
            f = {}  # pragma: no cover
        return await self._database.search(f, p, size)  # pragma: no cover
