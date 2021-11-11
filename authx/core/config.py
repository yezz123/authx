from string import ascii_letters, digits, punctuation
from typing import List

from starlette.config import Config

""" The Global Configuration for authx.
"""


config = Config()

JWT_ALGORITHM: str = config("JWT_ALGORITHM", cast=str, default="RS256")

DEBUG: bool = config("DEBUG", cast=bool, default=False)

LOGIN_RATELIMIT: int = config("LOGIN_RATELIMIT", cast=int, default=30)

EMAIL_CONFIRMATION_TIMEOUT: int = config(
    "EMAIL_CONFIRMATION_TIMEOUT", cast=int, default=1800
)
EMAIL_CONFIRMATION_MAX: int = config("EMAIL_CONFIRMATION_MAX", cast=int, default=2)

PASSWORD_RESET_TIMEOUT: int = config("PASSWORD_RESET_TIMEOUT", cast=int, default=1800)
PASSWORD_RESET_MAX: int = config("PASSWORD_RESET_MAX", cast=int, default=2)
PASSWORD_RESET_LIFETIME: int = config("PASSWORD_RESET_LIFETIME", cast=int, default=7200)

USERNAME_MIN_LENGTH: int = config("USERNAME_MIN_LENGTH", cast=int, default=3)
USERNAME_MAX_LENGTH: int = config("USERNAME_MAX_LENGTH", cast=int, default=20)

PASSWORD_MIN_LENGTH: int = config("PASSWORD_MIN_LENGTH", cast=int, default=6)
PASSWORD_MAX_LENGTH: int = config("PASSWORD_MAX_LENGTH", cast=int, default=32)


TIME_DELTA: int = config("TIME_DELTA", cast=int, default=3)


USERNAME_CHARS = "".join([ascii_letters, digits, " -_"])
PASSWORD_CHARS = "".join([ascii_letters, digits, punctuation])

WRONG_USERNAMES: List[str] = [
    "edit",
    "notifications",
    "settings",
    "message",
    "messages",
    "change_info",
]
