from typing import Any
from unittest import mock

import pytest
from fastapi import Depends, FastAPI, Request, Response
from fastapi.testclient import TestClient

from authx.cache.config import config
from authx.core.session import (
    SessionStorage,
    deleteSession,
    getSession,
    getSessionId,
    getSessionStorage,
    setSession,
)


@pytest.fixture
def sessionStorage():
    with mock.patch("authx.core.session.SessionStorage") as mockClass:
        mockStorage = mock.Mock(spec=SessionStorage)
        mockStorage.__setitem__ = mock.Mock()
        mockStorage.__getitem__ = mock.Mock()
        mockStorage.__delitem__ = mock.Mock()
        mockClass.return_value = mockStorage
        yield mockStorage


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
    client.post("/setSession", json=dict(a=1, b="data", c=True))
    sessionStorage.__setitem__.assert_called_once_with(
        sessionStorage.genSessionId(), dict(a=1, b="data", c=True)
    )

    sessionStorage.__getitem__.return_value = dict(a=1, b="data", c=True)
    client.get("/getSession", cookies={config.sessionIdName: "ssid"})
    sessionStorage.__getitem__.assert_called_once_with("ssid")

    client.post("/deleteSession", cookies={config.sessionIdName: "ssid"})
    sessionStorage.__delitem__.assert_called_once_with("ssid")
