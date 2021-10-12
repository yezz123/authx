import asyncio
import re
from datetime import datetime
from typing import Iterable, Optional, Tuple

from email_validator import EmailNotValidError, validate_email

from AuthX.core.config import (
    EMAIL_CONFIRMATION_MAX,
    EMAIL_CONFIRMATION_TIMEOUT,
    LOGIN_RATELIMIT,
    PASSWORD_RESET_LIFETIME,
    PASSWORD_RESET_MAX,
    PASSWORD_RESET_TIMEOUT,
)
from AuthX.core.logger import logger
from AuthX.database.mongodb import MongoDBBackend
from AuthX.database.redis import RedisBackend


class Base:
    """
    Initialize the API with the database and cache.

    :param database: The database to use.
    :param cache: The cache to use.
    :param callbacks: The callbacks to use.
    :param access_expiration: The expiration time for access tokens.

    :return: None
    """

    def __init__(
        self,
        database: MongoDBBackend,
        cache: RedisBackend,
        callbacks: Iterable,
        access_expiration: int = 60 * 60 * 6,
    ):
        """ Initialize the API with the database and cache.

        Args:
            database (MongoDBBackend): The database to use.
            cache (RedisBackend): The cache to use.
            callbacks (Iterable): The callbacks to use.
            access_expiration (int, optional): The expiration time for access tokens. Defaults to 60 * 60 * 6.
        """
        self._database: Optional[MongoDBBackend] = database
        self._cache: Optional[RedisBackend] = cache
        self._callbacks = callbacks
        self._access_expiration = access_expiration


class UsersCRUDMixin(Base):
    """ User CRUD MIXIN

    Args:
        Create all the Common CRUDS GET, POST, PUT, DELETE methods.
    """

    async def get(self, id: int) -> Optional[dict]:
        """
        Get a user by id.

        Args:
            id (int): The id of the user.

        Returns:
            Optional[dict]: The user.
        """
        return await self._database.get(id)

    async def get_by_email(self, email: str) -> Optional[dict]:
        """
        Get a user by email.

        Args:
            email (str): The email of the user.

        Returns:
            Optional[dict]: The user.
        """
        return await self._database.get_by_email(email)

    async def get_by_username(self, username: str) -> Optional[dict]:
        """
        Get a user by username.

        Args:
            username (str): The username of the user.

        Returns:
            Optional[dict]: The user.
        """
        return await self._database.get_by_username(username)

    async def get_by_social(self, provider: str, sid: str) -> Optional[dict]:
        """
        Get a user by social id.

        Args:
            provider (str): The provider of the social id.
            sid (str): The social id.

        Returns:
            Optional[dict]: The user.
        """
        return await self._database.get_by_social(provider, str(sid))

    async def get_by_login(self, login: str) -> Optional[dict]:
        """
        Get a user by login.

        Args:
            login (str): The login of the user.

        Returns:
            Optional[dict]: The user.
        """
        try:
            valid_email = validate_email(login).email
            return await self.get_by_email(valid_email)
        except EmailNotValidError:
            return await self.get_by_username(login)

    async def create(self, obj: dict) -> int:
        """
        Create a user.

        Args:
            obj (dict): The user to create.

        Returns:
            int: The id of the user.
        """
        return await self._database.create(obj)

    async def update(self, id: int, obj: dict) -> None:
        """
        Update a user.

        Args:
            id (int): The id of the user.
            obj (dict): The user to update.

        Returns:
            None
        """
        await self._database.update(id, obj)
        return None

    async def delete(self, id: int) -> None:
        """
        Delete a user.

        Args:
            id (int): The id of the user.

        Returns:
            None
        """
        await self._database.delete(id)
        return None

    async def update_last_login(self, id: int) -> None:
        """
        Update the last login of a user.

        Args:
            id (int): The id of the user.
        """
        await self.update(id, {"last_login": datetime.utcnow()})

    async def search(
        self, id: int, username: str, p: int, size: int
    ) -> Tuple[dict, int]:
        """
        Search for users.

        Args:
            id (int): The id of the user.
            username (str): The username of the user.
            p (int): The page number.
            size (int): The size of the page.

        Returns:
            Tuple[dict, int]: The users and the total number of users.
        """
        if id is not None:
            f = {"id": id}
        elif username is not None and username.strip() != "":
            f = {"username": re.compile(username, re.IGNORECASE)}  # type: ignore
        else:
            f = {}
        return await self._database.search(f, p, size)


class UsersProtectionMixin(Base):
    """ User Protection MIXIN

    Args:
        Create all the Common Protection GET, POST, PUT, DELETE methods.
    """

    async def _check_timeout_and_incr(self, key: str, max: int, timeout: int) -> bool:
        """
        Check if the timeout is expired and increment the counter.

        Args:
            key (str): The key to check.
            max (int): The maximum number of requests.
            timeout (int): The timeout in seconds.

        Returns:
            bool: True if the timeout is expired.
        """
        count = await self._cache.get(key)
        if count is not None:
            count = int(count)  # type: ignore
            if count >= max:  # type: ignore
                return False
            await self._cache.incr(key)
        else:
            await self._cache.set(key, 1, expire=timeout)

        return True

    async def is_bruteforce(self, ip: str, login: str) -> bool:
        """
        Check if the ip is in the bruteforce list.

        Args:
            ip (str): The ip to check.
            login (str): The login to check.

        Returns:
            bool: True if the ip is in the bruteforce list.
        """
        timeout_key = f"users:login:timeout:{ip}"
        timeout = await self._cache.get(timeout_key)

        if timeout is not None:
            return True

        rate_key = f"users:login:rate:{ip}"
        rate = await self._cache.get(rate_key)

        if rate is not None:
            rate = int(rate)  # type: ignore
            if rate > LOGIN_RATELIMIT:  # type: ignore
                await self._cache.set(timeout_key, 1, expire=60)
                logger.info(f"bruteforce_login ip={ip} login={login}")
                return True
        else:
            await self._cache.set(rate_key, 1, expire=60)

        await self._cache.incr(rate_key)
        return False


class UsersConfirmMixin(Base):
    """ User Confirmation MIXIN

    Args:
        Create all the Common Confirmation GET, POST, PUT, DELETE methods.
    """

    async def is_email_confirmation_available(self, id: int) -> bool:
        """
        Check if the email confirmation is available.

        Args:
            id (int): The id of the user.

        Returns:
            bool: True if the email confirmation is available.
        """
        key = f"users:confirm:count:{id}"
        return await self._check_timeout_and_incr(
            key, EMAIL_CONFIRMATION_MAX, EMAIL_CONFIRMATION_TIMEOUT
        )

    async def request_email_confirmation(self, email: str, token_hash: str) -> None:
        """
        Request an email confirmation.

        Args:
            email (str): The email of the user.
            token_hash (str): The token hash.

        Returns:
            None
        """
        await self._database.request_email_confirmation(email, token_hash)
        return None

    async def confirm_email(self, token_hash: str) -> bool:
        """
        Confirm an email.

        Args:
            token_hash (str): The token hash.

        Returns:
            bool: True if the email is confirmed.
        """
        return await self._database.confirm_email(token_hash)


class UsersUsernameMixin(Base):
    """ User Username MIXIN

    Args:
        Create all the Common Username GET, POST, PUT, DELETE methods.
    """

    async def change_username(self, id: int, new_username: str) -> None:
        """
        Change the username of a user.

        Args:
            id (int): The id of the user.
            new_username (str): The new username.
        """
        await self.update(id, {"username": new_username})
        for callback in self._callbacks:
            if isinstance(callback, str):
                await self._cache.dispatch_action(
                    f"chan:{callback}",
                    "CHANGE_USERNAME",
                    {"id": id, "username": new_username},
                )
            elif asyncio.iscoroutinefunction(callback):
                await callback(id, new_username)
            else:
                callback(id, new_username)


class UsersPasswordMixin(Base):
    """ User Password MIXIN

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
            return "set"
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
        if id is not None:
            return int(id)
        else:
            return None


class UsersManagementMixin(Base):
    """ User Management MIXIN

    Args:
        Create all the Common Management GET, POST, PUT, DELETE methods.
    """

    async def get_blacklist(self) -> dict:
        """
        Get the blacklist.

        Returns:
            dict: The blacklist.
        """
        blacklist_db = await self._database.get_blacklist()
        blacklist_cache = await self._cache.keys("users:blacklist:*")
        blacklist_cache_ids = []
        for key in blacklist_cache:
            _, _, id = key.split(":")
            blacklist_cache_ids.append(id)
        return {
            "global": [
                {"id": item.get("id"), "username": item.get("username")}
                for item in blacklist_db
            ],
            "current": blacklist_cache_ids,
        }

    async def toggle_blacklist(self, id: int) -> None:
        """
        Toggle the blacklist of a user.

        Args:
            id (int): The id of the user.

        Returns:
            None
        """
        item = await self.get(id)  # type: ignore
        active = item.get("active")
        await self.update(id, {"active": not active})
        key = f"users:blacklist:{id}"
        if active:
            await self._cache.set(key, 1, expire=self._access_expiration)
        else:
            await self._cache.delete(key)
        return None

    async def kick(self, id: int) -> None:
        """
        Kick a user.

        Args:
            id (int): The id of the user.
        """
        key = f"users:kick:{id}"
        now = int(datetime.utcnow().timestamp())

        await self._cache.set(key, now, expire=self._access_expiration)

    async def get_blackout(self) -> Optional[str]:
        """
        Get the blackout.

        Returns:
            Optional[str]: The blackout.
        """
        return await self._cache.get("users:blackout")

    async def set_blackout(self, ts: int) -> None:
        """
        Set the blackout.

        Args:
            ts (int): The timestamp.
        """
        await self._cache.set("users:blackout", ts)

    async def delete_blackout(self) -> None:
        """
        Delete the blackout.
        """
        await self._cache.delete("users:blackout")

    async def set_permissions(self) -> None:
        """
        Set the permissions.
        """


class UsersRepo(
    UsersCRUDMixin,
    UsersConfirmMixin,
    UsersPasswordMixin,
    UsersUsernameMixin,
    UsersProtectionMixin,
    UsersManagementMixin,
):
    """ User Repository

    Args:
        UsersCRUDMixin: CRUD methods
        UsersConfirmMixin: Confirmation methods
        UsersPasswordMixin: Password methods
        UsersUsernameMixin: Username methods
        UsersProtectionMixin: Protection methods
        UsersManagementMixin: Management methods
    """
