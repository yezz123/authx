from unittest import mock

import pytest
from fastapi import HTTPException

from authx.api import UsersRepo
from authx.services import AuthService
from authx.utils.strings import create_random_string, hash_string
from tests.utils import (
    MockAuthBackend,
    MockCacheBackend,
    MockDatabaseBackend,
    User,
    mock_verify_password,
    private_key,
    public_key,
)

admin = User(1, "admin", True)
user = User(2, "user", False)

RECAPTCHA_SECRET = "recaptcha_secret"

auth_backend = MockAuthBackend("RS256", private_key, public_key)


@pytest.fixture(autouse=True)
def auth_service_setup():
    """
    Setup the auth service
    """
    AuthService.setup(
        UsersRepo(MockDatabaseBackend("test"), MockCacheBackend(), []),
        auth_backend,
        False,
        "http://127.0.0.1",
        "127.0.0.1",
        RECAPTCHA_SECRET,
        None,
        None,
        None,
        None,
        None,
    )


CAPTCHA = "CAPTCHA"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email,username,password1,password2,valid_data,captcha,valid_captcha",
    [
        (
            "newuser2@gmail.com",
            "newuser2",
            "12345678",
            "12345678",
            True,
            CAPTCHA,
            False,
        ),
    ],
)
@mock.patch(
    "authx.services.auth.AuthService._request_email_confirmation",
    mock.AsyncMock(return_value=None),
)
async def test_register(
    email: str,
    username: str,
    password1: str,
    password2: str,
    valid_data: bool,
    captcha: str,
    valid_captcha: bool,
):
    """
    Test register
    Args:
        email (str): email
        username (str): username
        password1 (str): password
        password2 (str): password
        valid_data (bool): valid data
        captcha (str): captcha
        valid_captcha (bool): valid captcha
    """
    auth_service = AuthService()
    with mock.patch(
        "authx.services.auth.validate_captcha",
        mock.AsyncMock(return_value=valid_captcha),
    ) as mock_validate_captcha:
        if not valid_captcha:
            with pytest.raises(HTTPException) as e:
                await auth_service.register(
                    {
                        "email": email,
                        "username": username,
                        "password1": password1,
                        "password2": password2,
                        "captcha": captcha,
                    }
                )
            assert e.type is HTTPException
            assert e.value.args[0] == 400
        else:
            res = await auth_service.register(
                {
                    "email": email,
                    "username": username,
                    "password1": password1,
                    "password2": password2,
                    "captcha": captcha,
                }
            )
            assert isinstance(res, dict)
            assert isinstance(res.get("access"), str)
            assert isinstance(res.get("refresh"), str)

        mock_validate_captcha.assert_awaited_once_with(captcha, RECAPTCHA_SECRET)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "login,password",
    [
        ("user", "12345678"),
        ("admin", "12345678"),
        ("user@gmail.com", "12345678"),
        ("admin@gmail.com", "12345678"),
    ],
)
@mock.patch("authx.services.auth.verify_password", mock_verify_password)
async def test_login(login: str, password: str):
    """
    Test login
    Args:
        login (str): login
        password (str): password
    """
    auth_service = AuthService()
    tokens = await auth_service.login(
        {"login": login, "password": password}, "127.0.0.1"
    )
    assert isinstance(tokens, dict)


@pytest.mark.asyncio
async def test_refresh_access_token() -> str:
    auth_service = AuthService()
    refresh_token = auth_backend.create_refresh_token(
        {
            "id": 1,
            "username": "admin",
            "permissions": [],
            "type": "refresh",
        }
    )
    access_token = await auth_service.refresh_access_token(refresh_token)
    assert isinstance(access_token, str)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user,email,confirmed",
    [
        (
            User(2, "user", False),
            "user@gmail.com",
            True,
        ),
        (
            User(3, "anotheruser", False),
            "anotheruser@gmail.com",
            False,
        ),
    ],
)
async def test_get_email_confirmation_status(user: User, email: str, confirmed: bool):
    auth_service = AuthService()
    auth_service._user = user
    status = await auth_service.get_email_confirmation_status()
    assert status.get("email") == email
    assert status.get("confirmed") == confirmed

    auth_service._user = user
    status = await auth_service.get_email_confirmation_status()
    assert status.get("email") == email
    assert status.get("confirmed") is confirmed


@pytest.mark.asyncio
async def test_request_email_confirmation_confirmed():
    auth_service = AuthService()
    auth_service._user = User(2, "user", False)
    with pytest.raises(HTTPException) as e:
        await auth_service.request_email_confirmation()

    assert e.type is HTTPException
    assert e.value.args[0] == 400


@pytest.mark.asyncio
@mock.patch(
    "authx.services.auth.AuthService._request_email_confirmation",
    mock.AsyncMock(return_value=None),
)
async def test_request_email_confirmation():
    auth_service = AuthService()
    auth_service._user = User(3, "anotheruser", False)
    res = await auth_service.request_email_confirmation()
    assert res is None


@pytest.mark.asyncio
async def test_confirm_email():
    """ """
    auth_service = AuthService()
    email = "anotheruser@gmail.com"
    token = create_random_string()
    token_hash = hash_string(token)
    await auth_service._repo.request_email_confirmation(email, token_hash)

    with pytest.raises(HTTPException) as e:
        await auth_service.confirm_email("wrongtoken")

    assert e.type is HTTPException
    assert e.value.args[0] == 403

    await auth_service.confirm_email(token)

    item = await auth_service._repo.get_by_email(email)
    assert item.get("confirmed")
