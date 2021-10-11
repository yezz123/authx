from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from AuthX.routers import get_social_router
from tests.utils import ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME, MockAuthBackend

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="SECRET", max_age=10)

router = get_social_router(
    None,
    MockAuthBackend(None, None, None, None, None),
    False,
    "http://127.0.0.1",
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    None,
    None,
    ["google", "facebook", "vk"],
    {
        "google": {"id": "id", "secret": "secret",},
        "facebook": {"id": "id", "secret": "secret",},
    },
)


app.include_router(router, prefix="/auth")

test_client = TestClient(app)

ACCESS_TOKEN = "ACCESS"
REFRESH_TOKEN = "REFRESH"


@pytest.mark.parametrize("provider", ["google", "facebook"])
def test_login(provider: str):
    """
    Test login with social provider

    Args:
        provider (str): social provider
    """
    url = app.url_path_for("social:login", provider=provider)
    with mock.patch(
        f"AuthX.routers.social.SocialService.login_{provider}",
        mock.Mock(return_value="/"),
    ) as mock_method:
        # TODO: add test for redirect_url
        response = test_client.get(url, allow_redirects=False)
        mock_method.assert_called_once()

    assert response.status_code == 307


@pytest.mark.parametrize("provider", ["google", "facebook"])
@mock.patch(
    "AuthX.routers.social.check_state", mock.Mock(return_value=True),
)
def test_callback(provider: str):
    """
    Test callback with social provider
    Args:
        provider (str): social provider
    """
    patcher_callback = mock.patch(
        f"AuthX.routers.social.SocialService.callback_{provider}",
        mock.AsyncMock(return_value=(None, None,)),
    )
    mock_callback = patcher_callback.start()
    patcher_resolve_user = mock.patch(
        "AuthX.routers.social.SocialService.resolve_user",
        mock.AsyncMock(return_value={"access": ACCESS_TOKEN, "refresh": REFRESH_TOKEN}),
    )
    # TODO: add test for redirect_url
    mock_resolve_user = patcher_resolve_user.start()
    url = app.url_path_for("social:callback", provider=provider)
    response = test_client.get(url, allow_redirects=False)

    assert response.status_code == 307

    assert response.cookies.get(ACCESS_COOKIE_NAME) == ACCESS_TOKEN
    assert response.cookies.get(REFRESH_COOKIE_NAME) == REFRESH_TOKEN
    mock_callback.assert_awaited_once()
    mock_resolve_user.assert_awaited_once_with(provider, None, None)

    patcher_callback.stop()
    patcher_resolve_user.stop()
