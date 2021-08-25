from unittest import mock

from AuthX.routers import get_search_router
from fastapi import FastAPI
from fastapi.testclient import TestClient

from .utils import mock_admin_required

app = FastAPI()

router = get_search_router(None, mock_admin_required,)


app.include_router(router, prefix="/api")

test_client = TestClient(app)

ACCESS_TOKEN = "ACCESS"
REFRESH_TOKEN = "REFRESH"


def test_get_user():
    url = app.url_path_for("auth:get_user", id="1")
    with mock.patch(
        "AuthX.routers.search.SearchService.get_user",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.get(url)
        mock_method.assert_awaited_once_with(1)

    assert response.status_code == 200


def test_search():
    url = app.url_path_for("auth:search")
    with mock.patch(
        "AuthX.routers.search.SearchService.search", mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.get(f"{url}?id=1&username=admin&p=1")
        mock_method.assert_awaited_once_with(1, "admin", 1)

    assert response.status_code == 200
