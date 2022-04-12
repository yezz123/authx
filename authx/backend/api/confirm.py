from authx.backend.base import Base
from authx.core.config import EMAIL_CONFIRMATION_MAX, EMAIL_CONFIRMATION_TIMEOUT


class UsersConfirmMixin(Base):
    """User Confirmation MIXIN"""

    async def is_email_confirmation_available(self, id: int) -> bool:
        """Check if the email confirmation is available."""
        key = f"users:confirm:count:{id}"
        return await self._check_timeout_and_incr(
            key, EMAIL_CONFIRMATION_MAX, EMAIL_CONFIRMATION_TIMEOUT
        )

    async def request_email_confirmation(self, email: str, token_hash: str) -> None:
        """
        Request an email confirmation.
        """
        await self._database.request_email_confirmation(email, token_hash)
        return None

    async def confirm_email(self, token_hash: str) -> bool:
        """
        Confirm an email.
        """
        return await self._database.confirm_email(token_hash)
