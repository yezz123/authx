import datetime
import pickle
import random
from datetime import timedelta
from typing import Any
from unittest import mock
from unittest.mock import MagicMock

import pytest
from fastapi import Depends, FastAPI, Request, Response
from fastapi.testclient import TestClient
from redis import Redis

from authx._internal import basicConfig, config
from authx.external import (
    SessionStorage,
    deleteSession,
    getSession,
    getSessionId,
    getSessionStorage,
    setSession,
)


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


@pytest.fixture
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


@pytest.fixture
def sessionStorage():
    with mock.patch("authx.external.session.SessionStorage") as mockClass:
        mock_session_storage = MagicMock(spec=SessionStorage)
        mock_session_storage.__setitem__ = MagicMock()
        mock_session_storage.__getitem__ = MagicMock()
        mock_session_storage.__delitem__ = MagicMock()
        mockClass.return_value = mock_session_storage
        yield mock_session_storage


@pytest.fixture
def app(sessionStorage: SessionStorage):
    application = FastAPI(title=__name__)

    @application.post("/setSession")
    async def _setSession(
        request: Request,
        response: Response,
        sessionStorage: SessionStorage = Depends(getSessionStorage),
    ):
        sessionData = await request.json()
        setSession(response, sessionData, sessionStorage)

    @application.get("/getSession")
    async def _setSession(session: Any = Depends(getSession)):
        return session

    @application.post("/deleteSession")
    async def _deleteSession(
        sessionId: str = Depends(getSessionId),
        sessionStorage: SessionStorage = Depends(getSessionStorage),
    ):
        deleteSession(sessionId, sessionStorage)
        return None

    yield application


def testDeps(app: FastAPI, sessionStorage):
    client = TestClient(app)
    client.post("/setSession", json={"a": 1, "b": "data", "c": True})
    sessionStorage.__setitem__.assert_called_once()
    assert sessionStorage.__setitem__.call_args[0][0] == sessionStorage.genSessionId()
    assert sessionStorage.__setitem__.call_args[0][1] == {
        "a": 1,
        "b": "data",
        "c": True,
    }

    client.get("/getSession", cookies={config.sessionIdName: "test"})
    sessionStorage.__getitem__.assert_called_once()

    client.post("/deleteSession", cookies={config.sessionIdName: "test"})
    sessionStorage.__delitem__.assert_called_once()
