from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from AuthX.routers.social import get_router as get_social_router
from tests.utils import ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME, MockAuthBackend

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="SECRET", max_age=10)

router = get_social_router(
    None,
    MockAuthBackend(None, None, None),
    False,
    "http://127.0.0.1",
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    None,
    None,
    ["google", "facebook"],
    {
        "google": {"id": "id", "secret": "secret",},
        "facebook": {"id": "id", "secret": "secret",},
    },
    social_creds={"google": {"id": "id", "secret": "secret",},},
)


app.include_router(router, prefix="/auth")

test_client = TestClient(app)

ACCESS_TOKEN = "ACCESS"
REFRESH_TOKEN = "REFRESH"


@pytest.mark.parametrize("provider", ["google", "facebook"])
def test_login(provider: str):
    url = app.url_path_for("social:login", provider=provider)
    with mock.patch(
        f"AuthX.routers.social.SocialService.login_{provider}",
        mock.Mock(return_value="/"),
    ) as mock_method:
        response = test_client.get(url, allow_redirects=False)
        mock_method.assert_called_once()

    assert response.status_code == 307
