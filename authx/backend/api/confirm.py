from authx.backend.base import Base
from authx.core.config import EMAIL_CONFIRMATION_MAX, EMAIL_CONFIRMATION_TIMEOUT


class UsersConfirmMixin(Base):
    """User Confirmation MIXIN

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
