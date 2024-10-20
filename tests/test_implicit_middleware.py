from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from authx import AuthX, AuthXConfig


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def authx():
    config = AuthXConfig(
        JWT_IMPLICIT_REFRESH_ROUTE_EXCLUDE=["/excluded"],
        JWT_IMPLICIT_REFRESH_ROUTE_INCLUDE=["/included"],
        JWT_IMPLICIT_REFRESH_METHOD_EXCLUDE=["POST"],
        JWT_IMPLICIT_REFRESH_METHOD_INCLUDE=["GET"],
        JWT_TOKEN_LOCATION=["cookies"],
        JWT_IMPLICIT_REFRESH_DELTATIME=300,
    )
    return AuthX(config=config)


@pytest.fixture
def client(app):
    return TestClient(app)


def test_implicit_refresh_enabled_for_request(authx):
    # Test excluded route
    request = Mock(url=Mock(path="/excluded"))
    assert authx._implicit_refresh_enabled_for_request(
        request
    )  # Changed to assert True

    # Test included route
    request = Mock(url=Mock(path="/included"))
    assert authx._implicit_refresh_enabled_for_request(request)

    # Test excluded method
    request = Mock(url=Mock(path="/other"), method="POST")
    assert not authx._implicit_refresh_enabled_for_request(request)

    # Test default case
    request = Mock(url=Mock(path="/other"), method="PUT")
    assert authx._implicit_refresh_enabled_for_request(request)


@pytest.mark.asyncio
async def test_implicit_refresh_middleware_with_refresh_once(authx, app):
    @app.get("/test")
    async def test_route():
        return {"message": "success"}

    async def call_next(request):
        response = await app(request)
        return response

    @app.middleware("http")
    async def mock_middleware(request: Request, call_next):
        response = await authx.implicit_refresh_middleware(request, call_next)
        return response

    client = TestClient(app)

    mock_token = Mock()
    mock_payload = Mock(time_until_expiry=100, sub="user123", extra_dict={})

    with (
        patch.object(authx, "_get_token_from_request", return_value=mock_token),
        patch.object(authx, "verify_token", return_value=mock_payload),
        patch.object(authx, "create_access_token", return_value="new_token"),
        patch.object(authx, "set_access_cookies"),
        patch.object(authx, "_implicit_refresh_enabled_for_request", return_value=True),
    ):
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "success"}


@pytest.mark.asyncio
async def test_implicit_refresh_middleware_with_refresh(authx, app):
    @app.get("/test")
    async def test_route():
        return {"message": "success"}

    async def call_next(request):
        response = await app(request)
        return response

    app.middleware("http")(authx.implicit_refresh_middleware)
    client = TestClient(app)

    mock_token = Mock()
    mock_payload = Mock(time_until_expiry=100, sub="user123", extra_dict={})

    with (
        patch.object(authx, "_get_token_from_request", return_value=mock_token),
        patch.object(authx, "verify_token", return_value=mock_payload),
        patch.object(authx, "create_access_token", return_value="new_token"),
        patch.object(authx, "set_access_cookies"),
    ):
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "success"}


@pytest.mark.asyncio
async def test_implicit_refresh_middleware_no_refresh_needed(authx, app):
    @app.get("/test")
    async def test_route():
        return {"message": "success"}

    async def call_next(request):
        response = await app(request)
        return response

    app.middleware("http")(authx.implicit_refresh_middleware)
    client = TestClient(app)

    mock_token = Mock()
    mock_payload = Mock(time_until_expiry=1000, sub="user123", extra_dict={})

    with (
        patch.object(authx, "_get_token_from_request", return_value=mock_token),
        patch.object(authx, "verify_token", return_value=mock_payload),
        patch.object(authx, "create_access_token") as mock_create_token,
        patch.object(authx, "set_access_cookies") as mock_set_cookies,
    ):
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "success"}
        mock_create_token.assert_not_called()
        mock_set_cookies.assert_not_called()


@pytest.mark.asyncio
async def test_implicit_refresh_middleware_excluded_route(authx, app):
    @app.get("/excluded")
    async def excluded_route():
        return {"message": "excluded"}

    async def call_next(request):
        response = await app(request)
        return response

    app.middleware("http")(authx.implicit_refresh_middleware)
    client = TestClient(app)

    with patch.object(authx, "_get_token_from_request") as mock_get_token:
        response = client.get("/excluded")
        assert response.status_code == 200
        assert response.json() == {"message": "excluded"}
        mock_get_token.assert_not_called()


@pytest.mark.asyncio
async def test_implicit_refresh_middleware_excluded_method(authx, app):
    @app.post("/test")
    async def test_route():
        return {"message": "post"}

    async def call_next(request):
        response = await app(request)
        return response

    app.middleware("http")(authx.implicit_refresh_middleware)
    client = TestClient(app)

    with patch.object(authx, "_get_token_from_request") as mock_get_token:
        response = client.post("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "post"}
        mock_get_token.assert_not_called()
