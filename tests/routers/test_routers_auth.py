from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from authx.routers import get_auth_router
from tests.utils import (
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    MockAuthBackend,
    mock_get_authenticated_user,
    private_key,
    public_key,
)

app = FastAPI()

router = get_auth_router(
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
)


app.include_router(router)

test_client = TestClient(app)

ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"


@mock.patch(
    "authx.routers.auth.AuthService.register",
    mock.Mock(return_value={"access": ACCESS_TOKEN, "refresh": REFRESH_TOKEN}),
)
def test_register():
    """
    Test register
    """
    url = app.url_path_for("auth:register")
    data = {
        "email": "email@gmail.com",
        "username": "user12345",
        "password1": "12345678",
        "password2": "12345678",
    }
    response = test_client.post(
        url,
        json=data,
    )

    assert test_client.cookies.get(ACCESS_COOKIE_NAME) == ACCESS_TOKEN
    assert test_client.cookies.get(REFRESH_COOKIE_NAME) == REFRESH_TOKEN
    assert response.status_code == 200


@mock.patch(
    "authx.routers.auth.AuthService.login",
    mock.Mock(return_value={"access": ACCESS_TOKEN, "refresh": REFRESH_TOKEN}),
)
def test_login():
    """
    test login
    """
    url = app.url_path_for("auth:login")
    data = {
        "login": "login",
        "password": "password",
    }
    response = test_client.post(url, json=data)
    assert test_client.cookies.get(ACCESS_COOKIE_NAME) == ACCESS_TOKEN
    assert test_client.cookies.get(REFRESH_COOKIE_NAME) == REFRESH_TOKEN
    assert response.status_code == 200


def test_logout():
    """
    test logout
    """
    url = app.url_path_for("auth:logout")
    response = test_client.post(url)
    assert response.status_code == 200


def test_token():
    """
    test token
    """
    url = app.url_path_for("auth:token")
    response = test_client.post(url)
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == 2
    assert data.get("username") == "user"


@mock.patch(
    "authx.routers.auth.AuthService.refresh_access_token",
    mock.Mock(return_value=ACCESS_TOKEN),
)
def test_refresh_access_token():
    """
    test refresh access token
    """
    url = app.url_path_for("auth:refresh_access_token")

    response = test_client.post(url)
    assert response.status_code == 401
    # TODO test_client doesn't react to response.delete_cookie
    test_client.cookies.set(REFRESH_COOKIE_NAME, REFRESH_TOKEN)
    response = test_client.post(url)
    assert response.status_code == 200
    assert response.json().get("access") == ACCESS_TOKEN


@mock.patch(
    "authx.routers.auth.AuthService.get_email_confirmation_status",
    mock.Mock(return_value=None),
)
def test_get_email_confirmation_status():
    """
    test get email confirmation status
    """
    url = app.url_path_for("auth:get_email_confirmation_status")
    response = test_client.get(url)
    assert response.status_code == 200


@mock.patch(
    "authx.routers.auth.AuthService.request_email_confirmation",
    mock.Mock(return_value=None),
)
def test_request_email_confirmation():
    """
    test request email confirmation
    """
    url = app.url_path_for("auth:request_email_confirmation")
    response = test_client.post(url)
    assert response.status_code == 200


def test_confirm_email():
    """
    test confirm email
    """
    TOKEN = "123"
    url = app.url_path_for("auth:confirm_email", token=TOKEN)
    with mock.patch(
        "authx.routers.auth.AuthService.confirm_email",
        mock.Mock(return_value=None),
    ) as mock_method:
        response = test_client.post(url)
        mock_method.assert_awaited_once_with(TOKEN)
    assert response.status_code == 200


def test_change_username():
    """
    test change username
    """
    id = 2
    new_username = "new_username"
    url = app.url_path_for("auth:change_username", id=id)
    with mock.patch(
        "authx.routers.auth.AuthService.change_username",
        mock.Mock(return_value=None),
    ) as mock_method:
        response = test_client.post(url, json={"username": new_username})
        mock_method.assert_awaited_once_with(id, new_username)
    assert response.status_code == 200

    id = 1
    new_username = "new_admin"
    url = app.url_path_for("auth:change_username", id=id)
    response = test_client.post(url, json={"username": new_username})

    assert response.status_code == 403
