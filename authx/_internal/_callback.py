from typing import Generic, Optional

from authx.types import ModelCallback, T, TokenCallback


class _CallbackHandler(Generic[T]):
    """
    Base class for callback handlers in AuthX.

    Args:
        Generic (T): Model type

    Raises:
        AttributeError: If callback is not set
    """

    def __init__(self, model: T) -> None:
        """Base class for callback handlers in AuthX.

        Args:
            model (T): Model instance
        """
        self._model: T = model
        self.callback_get_model_instance: Optional[ModelCallback[T]] = None
        self.callback_is_token_in_blocklist: Optional[TokenCallback] = None

        # Exceptions
        self._callback_model_set_exception = AttributeError(
            f"Model callback not set for {self._model.__class__.__name__} instance"
        )
        self._callback_token_set_exception = AttributeError(
            f"Token callback not set for {self._model.__class__.__name__} instance"
        )

    @property
    def is_model_callback_set(self) -> bool:
        """Check if callback is set for model instance"""
        return self.callback_get_model_instance is not None

    @property
    def is_token_callback_set(self) -> bool:
        """Check if callback is set for token"""
        return self.callback_is_token_in_blocklist is not None

    def _check_model_callback_is_set(self, ignore_errors: bool = False) -> bool:
        """Check if callback is set for model instance and raise exception if not set"""
        if self.is_model_callback_set:
            return True
        if not ignore_errors:
            raise self._callback_model_set_exception
        return False

    def _check_token_callback_is_set(self, ignore_errors: bool = False) -> bool:
        """Check if callback is set for token and raise exception if not set"""
        if self.is_token_callback_set:
            return True
        if not ignore_errors:
            raise self._callback_token_set_exception
        return False

    def set_callback_get_model_instance(self, callback: ModelCallback[T]) -> None:
        """Set callback for model instance"""
        self.callback_get_model_instance = callback

    def set_callback_token_blocklist(self, callback: TokenCallback) -> None:
        """Set callback for token"""
        self.callback_is_token_in_blocklist = callback

    def _get_current_subject(self, uid: str, **kwargs) -> T:
        """Get current model instance from callback"""
        self._check_model_callback_is_set()
        callback: ModelCallback[T] = self.callback_get_model_instance
        return callback(uid, **kwargs)

    def is_token_in_blocklist(self, token: str, **kwargs) -> bool:
        """Check if token is in blocklist"""
        if self._check_token_callback_is_set(ignore_errors=True):
            callback: TokenCallback = self.callback_is_token_in_blocklist
            return callback(token, **kwargs)
        return False
