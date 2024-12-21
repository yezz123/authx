import pytest
from fastapi.testclient import TestClient
from httpx import Response

from authx import AuthXConfig
from tests.utils import (
    create_blocklist_routes,
    create_get_token_routes,
    create_protected_routes,
    create_secure_routes,
    create_securities,
    create_subject_routes,
    create_token_routes,
    init_app,
)


@pytest.fixture(scope="function")
def config():
    """Fixture for AuthX Configuration."""
    return AuthXConfig(
        JWT_SECRET_KEY="secret",
        JWT_TOKEN_LOCATION=["headers", "json", "query", "cookies"],
    )


@pytest.fixture(scope="function")
def api(config: AuthXConfig):
    """Fixture for FastAPI TestClient."""
    app, security = init_app(config=config)
    create_protected_routes(app, security)
    create_token_routes(app, security)
    create_blocklist_routes(app, security)
    create_get_token_routes(app, security)
    create_subject_routes(app, security)
    create_secure_routes(app, create_securities(security))
    return TestClient(app)


@pytest.fixture(scope="function")
def no_csrf_api():
    """Fixture for FastAPI TestClient with CSRF Protection disabled."""
    app, security = init_app(
        config=AuthXConfig(
            JWT_COOKIE_CSRF_PROTECT=False,
            JWT_SECRET_KEY="secret",
            JWT_TOKEN_LOCATION=["headers", "json", "query", "cookies"],
        )
    )
    create_protected_routes(app, security)
    create_token_routes(app, security)
    create_blocklist_routes(app, security)
    create_get_token_routes(app, security)
    create_subject_routes(app, security)
    create_secure_routes(app, create_securities(security))
    return TestClient(app)


@pytest.fixture(scope="function")
def access_response(api: TestClient):
    """Fixture for Access Token Response."""
    return api.get("/token/access")


@pytest.fixture(scope="function")
def access_token(access_response: Response) -> str:
    """Fixture for Access Token."""
    assert access_response.status_code == 200
    return access_response.json()["token"]


@pytest.fixture(scope="function")
def access_csrf_token(access_response: Response, config: AuthXConfig) -> str:
    """Fixture for Access CSRF Token."""
    assert access_response.status_code == 200
    return access_response.cookies.get(config.JWT_ACCESS_CSRF_COOKIE_NAME)


@pytest.fixture(scope="function")
def refresh_response(api: TestClient):
    """Fixture for Refresh Token Response."""
    return api.get("/token/refresh")


@pytest.fixture(scope="function")
def refresh_token(refresh_response: Response) -> str:
    """Fixture for Refresh Token."""
    assert refresh_response.status_code == 200
    return refresh_response.json()["token"]


@pytest.fixture(scope="function")
def refresh_csrf_token(refresh_response: Response, config: AuthXConfig) -> str:
    """Fixture for Refresh CSRF Token."""
    assert refresh_response.status_code == 200
    return refresh_response.cookies.get(config.JWT_REFRESH_CSRF_COOKIE_NAME)


@pytest.fixture(scope="function")
def fresh_response(api: TestClient) -> Response:
    """Fixture for Fresh Token Response."""
    return api.get("/token/fresh")


@pytest.fixture(scope="function")
def fresh_token(fresh_response: Response) -> str:
    """Fixture for Fresh Token."""
    assert fresh_response.status_code == 200
    return fresh_response.json()["token"]


@pytest.fixture(scope="function")
def fresh_csrf_token(fresh_response: Response, config: AuthXConfig) -> str:
    """Fixture for Fresh CSRF Token."""
    assert fresh_response.status_code == 200
    return fresh_response.cookies.get(config.JWT_ACCESS_CSRF_COOKIE_NAME)
