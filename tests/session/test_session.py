import datetime
import pickle
from unittest import mock

import pytest
from redis import Redis

from authx.external import SessionStorage


@pytest.fixture(scope="module")
def sessionStorage():
    storage = SessionStorage()
    storage.client = mock.Mock(spec=Redis)
    yield storage


def testSessionStorage(sessionStorage: SessionStorage):
    callTimes = 0

    def getStub(*_, **__):
        nonlocal callTimes
        callTimes += 1

        if callTimes < 2:
            return pickle.dumps({"a": 1}, protocol=pickle.HIGHEST_PROTOCOL)
        return None

    data = {"a": 1, "b": "data", "c": True}
    sessionStorage.client.get = getStub
    sessionId = sessionStorage.genSessionId()

    sessionStorage[sessionId] = data
    sessionStorage.client.set.assert_called_once_with(
        sessionId,
        pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL),
        ex=datetime.timedelta(seconds=21600),
    )

    sessionStorage.client.get = mock.Mock(return_value=pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL))
    assert sessionStorage[sessionId] == data

    sessionStorage.client.get.assert_called_with(sessionId)

    del sessionStorage[sessionId]
    sessionStorage.client.delete.assert_called_once_with(sessionId)
