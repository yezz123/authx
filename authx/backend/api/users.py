import asyncio

from authx.backend.base import Base


class UsersUsernameMixin(Base):
    """User Username MIXIN

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
        await self.update(id, {"username": new_username})  # pragma: no cover
        for callback in self._callbacks:  # pragma: no cover
            if isinstance(callback, str):  # pragma: no cover
                await self._cache.dispatch_action(
                    f"chan:{callback}",
                    "CHANGE_USERNAME",
                    {"id": id, "username": new_username},
                )  # pragma: no cover
            elif asyncio.iscoroutinefunction(callback):  # pragma: no cover
                await callback(id, new_username)  # pragma: no cover
            else:  # pragma: no cover
                callback(id, new_username)  # pragma: no cover
