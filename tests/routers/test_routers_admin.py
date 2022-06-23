from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from authx import get_admin_router
from tests.utils import mock_admin_required

app = FastAPI()

router = get_admin_router(
    None,
    mock_admin_required,
)


app.include_router(router)

test_client = TestClient(app)

ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"


def test_get_blacklist():
    url = app.url_path_for("admin:get_blacklist")
    with mock.patch(
        "authx.routers.admin.AdminService.get_blacklist",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.get(url)
        mock_method.assert_awaited_once()

    assert response.status_code == 200


def test_toggle_blacklist():
    url = app.url_path_for("admin:toggle_blacklist", id="5")
    with mock.patch(
        "authx.routers.admin.AdminService.toggle_blacklist",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.post(url)
        mock_method.assert_awaited_once_with(5)

    assert response.status_code == 200


def test_get_blackout():
    url = app.url_path_for("admin:get_blackout")
    with mock.patch(
        "authx.routers.admin.AdminService.get_blackout",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.get(url)
        mock_method.assert_awaited_once()

    assert response.status_code == 200


def test_set_blackout():
    url = app.url_path_for("admin:set_blackout")
    with mock.patch(
        "authx.routers.admin.AdminService.set_blackout",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.post(url)
        mock_method.assert_awaited_once()

    assert response.status_code == 200


def test_delete_blackout():
    url = app.url_path_for("admin:delete_blackout")
    with mock.patch(
        "authx.routers.admin.AdminService.delete_blackout",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.delete(url)
        mock_method.assert_awaited_once()

    assert response.status_code == 200


def test_get_id_by_username():
    url = app.url_path_for("admin:get_id_by_username")
    with mock.patch(
        "authx.routers.admin.AdminService.get_id_by_username",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.get(f"{url}?username=admin")
        mock_method.assert_awaited_once_with("admin")

    assert response.status_code == 200


def test_kick():
    url = app.url_path_for("admin:kick", id="5")
    with mock.patch(
        "authx.routers.admin.AdminService.kick",
        mock.AsyncMock(return_value=None),
    ) as mock_method:
        response = test_client.post(url)
        mock_method.assert_awaited_once_with(5)

    assert response.status_code == 200
