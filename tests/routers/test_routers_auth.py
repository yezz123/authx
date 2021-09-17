from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from AuthX.routers.auth import get_router as get_auth_router
from tests.utils import (
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    MockAuthBackend,
    mock_get_authenticated_user,
)

app = FastAPI()

router = get_auth_router(
    None,
    MockAuthBackend("RS256"),
    mock_get_authenticated_user,
    True,
    "http://127.0.0.1",
    "127.0.0.1",
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    60 * 5,
    60 * 10,
    None,
    None,
    None,
    None,
    None,
    None,
    display_name="auth",
)


app.include_router(router)

test_client = TestClient(app)

ACCESS_TOKEN = "ACCESS"
REFRESH_TOKEN = "REFRESH"


def test_token():
    url = app.url_path_for("auth:token")
    response = test_client.post(url)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == 2  # TODO
    assert data.get("username") == "user"  # TODO


@mock.patch(
    "AuthX.routers.auth.AuthService.get_email_confirmation_status",
    mock.AsyncMock(return_value=None),
)
def test_get_email_confirmation_status():
    url = app.url_path_for("auth:get_email_confirmation_status")
    response = test_client.get(url)
    assert response.status_code == 200


@mock.patch(
    "AuthX.routers.auth.AuthService.request_email_confirmation",
    mock.AsyncMock(return_value=None),
)
def test_request_email_confirmation():
    url = app.url_path_for("auth:request_email_confirmation")
    response = test_client.post(url)
    assert response.status_code == 200


def test_confirm_email():
    TOKEN = "123"
    url = app.url_path_for("auth:confirm_email", token=TOKEN)
    with mock.patch(
        "AuthX.routers.auth.AuthService.confirm_email",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.post(url)
        mock_method.assert_awaited_once_with(TOKEN)
    assert response.status_code == 200


def test_change_username():  # TODO

    id = 2
    new_username = "new_username"
    url = app.url_path_for("auth:change_username", id=id)
    with mock.patch(
        "AuthX.routers.auth.AuthService.change_username",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.post(url, json={"username": new_username})
        mock_method.assert_awaited_once_with(id, new_username)
    assert response.status_code == 200

    id = 1
    new_username = "new_admin"
    url = app.url_path_for("auth:change_username", id=id)
    response = test_client.post(url, json={"username": new_username})

    assert response.status_code == 403
