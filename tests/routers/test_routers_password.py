from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from authx.routers import get_password_router
from tests.utils import (
    MockAuthBackend,
    mock_get_authenticated_user,
    private_key,
    public_key,
)

app = FastAPI()

router = get_password_router(
    None,
    MockAuthBackend(
        "RS256",
        private_key,
        public_key,
    ),
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
    """
    test forgot password
    """
    url = app.url_path_for("auth:forgot_password")
    with mock.patch(
        "authx.routers.password.PasswordService.forgot_password",
        mock.Mock(return_value=None),
    ) as mock_method:
        response = test_client.post(
            url,
            json={
                "email": "user@gmail.com",
            },
        )
        mock_method.assert_awaited_once()
    assert response.status_code == 200


def test_password_status():
    """
    test password status
    """
    url = app.url_path_for("auth:password_status")
    with mock.patch(
        "authx.routers.password.PasswordService.password_status",
        mock.Mock(return_value=None),
    ) as mock_method:
        response = test_client.get(url)

        mock_method.assert_awaited_once()
    assert response.status_code == 200


def test_password_set():
    """
    test password set
    """
    url = app.url_path_for("auth:password_set")
    with mock.patch(
        "authx.routers.password.PasswordService.password_set",
        mock.Mock(return_value=None),
    ) as mock_method:
        response = test_client.post(
            url,
            json={
                "password1": "12345678",
                "password2": "12345678",
            },
        )

        mock_method.assert_awaited_once()

    assert response.status_code == 200


def test_password_reset():
    """
    Test password reset
    """
    url = app.url_path_for("auth:password_reset", token="TOKEN")
    with mock.patch(
        "authx.routers.password.PasswordService.password_reset",
        mock.Mock(return_value=None),
    ) as mock_method:
        response = test_client.post(
            url,
            json={
                "password1": "12345678",
                "password2": "12345678",
            },
        )

        mock_method.assert_awaited_once()

    assert response.status_code == 200


def test_password_change():
    """
    test password change
    """
    url = app.url_path_for("auth:password_change")
    with mock.patch(
        "authx.routers.password.PasswordService.password_change",
        mock.Mock(return_value=None),
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
