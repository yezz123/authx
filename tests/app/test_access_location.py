from authx.config import AuthXConfig


def test_access_location_headers(api, access_token: str):
    response = api.post(
        "/read/access", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.json()["location"] == "headers"
    assert response.json()["type"] == "access"


def test_access_location_json(api, access_token: str, config: AuthXConfig):
    response = api.post("/read/access", json={config.JWT_JSON_KEY: access_token})
    assert response.json()["location"] == "json"
    assert response.json()["type"] == "access"


def test_access_location_query(api, access_token: str, config: AuthXConfig):
    response = api.post(
        "/read/access", params={config.JWT_QUERY_STRING_NAME: access_token}
    )
    assert response.json()["location"] == "query"
    assert response.json()["type"] == "access"


def test_access_location_cookies(
    api, access_token: str, access_csrf_token: str, config: AuthXConfig
):
    response = api.post(
        "/read/access",
        cookies={config.JWT_ACCESS_COOKIE_NAME: access_token},
        headers={config.JWT_ACCESS_CSRF_HEADER_NAME: access_csrf_token},
    )
    assert response.json()["location"] == "cookies"
    assert response.json()["type"] == "access"


def test_access_location_cookies_no_csrf(api, access_token: str, config: AuthXConfig):
    response = api.post(
        "/read/access",
        cookies={config.JWT_ACCESS_COOKIE_NAME: access_token},
    )
    assert response.json() is None


def test_access_location_cookies_disabled_csrf(no_csrf_api, config: AuthXConfig):
    response = no_csrf_api.get("/token/access")

    access_token = response.json()["token"]

    response = no_csrf_api.post(
        "/read/access",
        cookies={config.JWT_ACCESS_COOKIE_NAME: access_token},
    )
    assert response.json()["location"] == "cookies"
    assert response.json()["type"] == "access"
