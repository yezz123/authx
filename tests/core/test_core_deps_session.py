from typing import Any
from unittest import mock
from unittest.mock import MagicMock

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
    client.post("/setSession", json=dict(a=1, b="data", c=True))
    sessionStorage.__setitem__.assert_called_once()
    assert sessionStorage.__setitem__.call_args[0][0] == sessionStorage.genSessionId()
    assert sessionStorage.__setitem__.call_args[0][1] == dict(a=1, b="data", c=True)

    client.get("/getSession", cookies={config.sessionIdName: "test"})
    sessionStorage.__getitem__.assert_called_once()

    client.post("/deleteSession", cookies={config.sessionIdName: "test"})
    sessionStorage.__delitem__.assert_called_once()
    assert sessionStorage.__delitem__.call_args[0][0] == "test"
