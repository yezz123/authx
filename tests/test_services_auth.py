from unittest import mock

import pytest
from fastapi import HTTPException

from AuthX.api import UsersRepo
from AuthX.services import AuthService
from AuthX.utils.strings import create_random_string, hash_string

from .utils import (
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

RECAPTCHA_SECRET = "RECAPTCHA_SECRET"

auth_backend = MockAuthBackend("RS256", private_key, public_key)


@pytest.fixture(autouse=True)
def auth_service_setup():
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
            "newuser1@gmail.com",
            "newuser1",
            "12345678",
            "12345678",
            True,
            CAPTCHA,
            True,
        ),
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
    "AuthX.services.auth.AuthService._request_email_confirmation",
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
    auth_service = AuthService()
    with mock.patch(
        "AuthX.services.auth.validate_captcha",
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
    # TODO: data


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
@mock.patch("AuthX.services.auth.verify_password", mock_verify_password)
async def test_login(login: str, password: str):
    auth_service = AuthService()
    tokens = await auth_service.login(
        {"login": login, "password": password}, "127.0.0.1"
    )
    # TODO
    assert isinstance(tokens, dict)


@pytest.mark.asyncio
async def test_refresh_access_token() -> str:
    auth_service = AuthService()
    refresh_token = auth_backend.create_refresh_token(
        {"id": 1, "username": "admin", "permissions": [], "type": "refresh",}
    )
    access_token = await auth_service.refresh_access_token(refresh_token)
    assert isinstance(access_token, str)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user,email,confirmed",
    [
        (User(2, "user", False), "user@gmail.com", True,),
        (User(3, "anotheruser", False), "anotheruser@gmail.com", False,),
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
    "AuthX.services.auth.AuthService._request_email_confirmation",
    mock.AsyncMock(return_value=None),
)
async def test_request_email_confirmation():
    auth_service = AuthService()
    auth_service._user = User(3, "anotheruser", False)
    res = await auth_service.request_email_confirmation()
    assert res is None


@pytest.mark.asyncio
async def test_confirm_email():
    auth_service = AuthService()
    email = "anotheruser@gmail.com"
    token = create_random_string()
    token_hash = hash_string(token)
    await auth_service._repo.request_email_confirmation(email, token_hash)

    with pytest.raises(HTTPException) as e:
        await auth_service.confirm_email("wrongtoken")

    assert e.type is HTTPException
    assert e.value.args[0] == 403  # TODO: 400 maybe

    await auth_service.confirm_email(token)

    item = await auth_service._repo.get_by_email(email)
    assert item.get("confirmed")


@pytest.mark.asyncio
async def test_change_username():
    auth_service = AuthService(User(1, "admin", True))
    await auth_service.change_username(2, "newusername")  # admin
    assert await auth_service._repo.get_by_username("newusername") is not None
    assert await auth_service._repo.get_by_username("username") is None

    with pytest.raises(HTTPException) as e:
        await auth_service.change_username(2, "admin")  # exists

    assert e.type is HTTPException
    assert e.value.args[0] == 400

    with pytest.raises(HTTPException) as e:
        await auth_service.change_username(1, "admin")  # same

    assert e.type is HTTPException
    assert e.value.args[0] == 400

    await auth_service.change_username(1, "newadmin")  # own
    assert await auth_service._repo.get_by_username("newadmin") is not None
    assert await auth_service._repo.get_by_username("admin") is None
