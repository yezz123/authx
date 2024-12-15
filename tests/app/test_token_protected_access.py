import pytest

import authx.exceptions as exc
from authx.config import AuthXConfig


def test_no_token_protected_access(api):
    with pytest.raises(exc.MissingTokenError):
        api.post("/protected/access")


def test_fresh_token_protected_access_headers(api, fresh_token: str):
    response = api.post("/protected/access", headers={"Authorization": f"Bearer {fresh_token}"})
    assert response.status_code == 200


def test_refresh_token_protected_access_headers(api, refresh_token: str):
    with pytest.raises(exc.AccessTokenRequiredError):
        api.post("/protected/access", headers={"Authorization": f"Bearer {refresh_token}"})


def test_access_token_protected_access_headers(api, access_token: str):
    response = api.post("/protected/access", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


def test_access_token_protected_access_json(api, config: AuthXConfig, access_token: str):
    response = api.post("/protected/access", json={config.JWT_JSON_KEY: access_token})
    assert response.status_code == 200


def test_access_token_protected_access_query(api, config: AuthXConfig, access_token: str):
    response = api.post("/protected/access", params={config.JWT_QUERY_STRING_NAME: access_token})
    assert response.status_code == 200


def test_access_token_protected_access_cookies_no_csrf(api, config: AuthXConfig):
    response = api.get("/token/access")
    assert response.status_code == 200
    assert "token" in response.json()
    access_token = response.json()["token"]

    response = api.post("/read/access", headers={"Authorization": f"Bearer {access_token}"})

    with pytest.raises(exc.MissingTokenError) as err:
        api.post(
            "/protected/access",
            cookies={config.JWT_ACCESS_COOKIE_NAME: access_token},
            headers={"Content-Type": "application/json"},
        )

    assert "Missing CSRF token" in err.value.args


def test_access_token_protected_access_cookies_csrf_cookies(
    api, config: AuthXConfig, access_token: str, access_csrf_token: str
):
    response = api.post(
        "/protected/access",
        cookies={
            config.JWT_ACCESS_COOKIE_NAME: access_token,
        },
        headers={config.JWT_ACCESS_CSRF_HEADER_NAME: access_csrf_token},
    )
    assert response.status_code == 200
