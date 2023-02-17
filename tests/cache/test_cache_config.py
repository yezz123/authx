import random
from datetime import timedelta

from authx.cache.config import basicConfig, config


def test_config() -> None:
    session_id = config.genSessionId().isnumeric()
    assert session_id is not None


def testBasicConfig():
    origin = config.settings["sessionIdGenerator"]
    basicConfig(
        redisURL="redis://localhost:6379/1",
        sessionIdName="sessionId",
        sessionIdGenerator=lambda: str(random.randint(1000, 9999)),
        expireTime=timedelta(days=1),
    )
    assert config.redisURL == "redis://localhost:6379/1"
    assert config.sessionIdName == "sessionId"
    assert config.genSessionId().isnumeric()
    assert config.expireTime == timedelta(seconds=24 * 3600)

    basicConfig(sessionIdGenerator=origin, expireTime=timedelta(hours=6))
