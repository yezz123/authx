from AuthX.core.config import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)


class ErrorMessages:
    """
    Setup Error Messages for Services & routers (for example: "password mismatch")
    """

    def __init__(self,):
        """
        Initialize Error Messages
        """
        self._full_messages = {
            """
        Create Error Messages for Services & models.
        """
            # models
            "username length": f"Username must contain from {USERNAME_MIN_LENGTH} to {USERNAME_MAX_LENGTH} symbols",
            "username special characters": "Username must not contain special characters",
            "username wrong": "Wrong username",
            "username different letters": "Username must be only in latin or cyrillic",
            "password space": "Password must not contain spaces",
            "password length": f"Password must contain from {PASSWORD_MIN_LENGTH} to {PASSWORD_MAX_LENGTH} symbols",
            "password mismatch": "Passwords mismatch",
            "password special": "Password must contain only letters, numbers and #$%&'()*+,-./:;<=>?@[]^_`{|}~",
            # services
            "existing email": "Email already exists",
            "existing username": "Username already exists",
            "ban": "User is banned",
            "reset before": "You can send another email in 30 minutes",
            "captcha": "Wrong captcha",
            "validation": "Check data",
            "password already exists": "Password exists",
            "password invalid": "Wrong password!",
            "username change same": "Enter NEW username",
            "server error": "Unknown error",
            "try another email": "Try another email",
        }
        """
        Create a Server Error Message
        """
        self._server_error = "Unknown error"

    def get_error_message(self, msg: str) -> str:
        return self._full_messages.get(msg) or self._server_error


def get_error_message(msg: str) -> str:
    error_messages = ErrorMessages()
    return error_messages.get_error_message(msg)
