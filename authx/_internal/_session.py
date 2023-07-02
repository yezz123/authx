from datetime import timedelta
from typing import Callable, Dict, Optional
from uuid import uuid4

from pydantic import BaseSettings


def genSessionId() -> str:
    return uuid4().hex


settings: Dict[str, Callable[[], str]] = {"sessionIdGenerator": genSessionId}


class Config(BaseSettings):
    redisURL: str = "redis://localhost:6379/0"
    settings: Dict[str, Callable[[], str]] = settings
    sessionIdName: str = "ssid"
    expireTime: timedelta = timedelta(hours=6)

    def genSessionId(self) -> str:
        return self.settings["sessionIdGenerator"]()


config = Config()


def basicConfig(
    redisURL: Optional[str] = "",
    sessionIdName: Optional[str] = "",
    sessionIdGenerator: Optional[Callable[[], str]] = None,
    expireTime: Optional[timedelta] = None,
) -> None:
    if redisURL:
        config.redisURL = redisURL
    if sessionIdName:
        config.sessionIdName = sessionIdName
    if sessionIdGenerator:
        config.settings["sessionIdGenerator"] = sessionIdGenerator
    if expireTime:
        config.expireTime = expireTime
