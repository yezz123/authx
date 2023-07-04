import random
from datetime import timedelta
from unittest import mock

from authx._internal import config


@mock.patch("authx._internal._session.uuid4")
def testConfig(mock_uuid4):
    config().genSessionId()
    mock_uuid4.assert_called_once_with()


def testBasicConfig():
    config(
        redisURL="redis://localhost:6379/1",
        sessionIdName="sessionId",
        sessionIdGenerator=lambda: str(random.randint(1000, 9999)),
        expireTime=timedelta(days=1),
    )
    assert config().redisURL == "redis://localhost:6379/1"
    assert config().sessionIdName == "sessionId"
    assert config().genSessionId().isnumeric()
    assert config().expireTime == timedelta(seconds=24 * 3600)
