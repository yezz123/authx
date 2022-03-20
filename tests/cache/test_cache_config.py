import random
import unittest
from datetime import timedelta
from unittest import mock

from authx.cache.config import basicConfig, config


@unittest.skip(
    "Improve this test later while getting issues after adding the container of Redis to Github Workflow"
)
@mock.patch("authx.cache.config.uuid4")
def testConfig(mock_uuid4):
    config.genSessionId()
    mock_uuid4.assert_called_once_with()  # pragma: no cover


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
