from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from AuthX.routers.password import get_router as get_password_router
from tests.utils import (
    MockAuthBackend,
    mock_get_authenticated_user,
)

app = FastAPI()

router = get_password_router(
    None,
    MockAuthBackend("RS256"),
    mock_get_authenticated_user,
    True,
    "http://127.0.0.1",
    "127.0.0.1",
    None,
    None,
    None,
    None,
    None,
    None,
)

app.include_router(router)

test_client = TestClient(app)


def test_forgot_password():
    url = app.url_path_for("auth:forgot_password")
    with mock.patch(
        "AuthX.routers.password.PasswordService.forgot_password",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.post(url, json={"email": "user@gmail.com",},)
        mock_method.assert_awaited_once()
    assert response.status_code == 200


def test_password_status():
    url = app.url_path_for("auth:password_status")
    with mock.patch(
        "AuthX.routers.password.PasswordService.password_status",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.get(url)

        mock_method.assert_awaited_once()
    assert response.status_code == 200


def test_password_set():
    url = app.url_path_for("auth:password_set")
    with mock.patch(
        "AuthX.routers.password.PasswordService.password_set",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.post(
            url, json={"password1": "12345678", "password2": "12345678",},
        )

        mock_method.assert_awaited_once()

    assert response.status_code == 200


def test_password_reset():
    url = app.url_path_for("auth:password_reset", token="TOKEN")
    with mock.patch(
        "AuthX.routers.password.PasswordService.password_reset",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.post(
            url, json={"password1": "12345678", "password2": "12345678",},
        )

        mock_method.assert_awaited_once()

    assert response.status_code == 200


def test_password_change():
    url = app.url_path_for("auth:password_change")
    with mock.patch(
        "AuthX.routers.password.PasswordService.password_change",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.put(
            url,
            json={
                "old_password": "87654321",
                "password1": "12345678",
                "password2": "12345678",
            },
        )

        mock_method.assert_awaited_once()

    assert response.status_code == 200
