from authx.config import AuthXConfig


def assert_auth_error(response, error_type: str, message: str):
    assert response.status_code == 401
    assert response.json() == {"message": message, "error_type": error_type}


def test_no_token_protected_fresh(api):
    response = api.post("/protected/fresh")
    assert_auth_error(response, "MissingTokenError", "Token Error")


def test_access_fresh_token_protected_fresh(api, access_token: str):
    response = api.post("/protected/fresh", headers={"Authorization": f"Bearer {access_token}"})
    assert_auth_error(response, "FreshTokenRequiredError", "Fresh token required")


def test_refresh_fresh_token_protected_fresh(api, refresh_token: str):
    response = api.post("/protected/fresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert_auth_error(response, "AccessTokenRequiredError", "Access token required")


def test_fresh_token_protected_fresh_headers(api, fresh_token: str):
    response = api.post("/protected/fresh", headers={"Authorization": f"Bearer {fresh_token}"})
    assert response.status_code == 200


def test_fresh_token_protected_fresh_json(api, config: AuthXConfig, fresh_token: str):
    response = api.post("/protected/fresh", json={config.JWT_JSON_KEY: fresh_token})
    assert response.status_code == 200


def test_fresh_token_protected_fresh_query(api, config: AuthXConfig, fresh_token: str):
    response = api.post("/protected/fresh", params={config.JWT_QUERY_STRING_NAME: fresh_token})
    assert response.status_code == 200


def test_fresh_token_protected_fresh_cookies_csrf_cookies(
    api, config: AuthXConfig, fresh_token: str, fresh_csrf_token: str
):
    response = api.post(
        "/protected/access",
        cookies={
            config.JWT_ACCESS_COOKIE_NAME: fresh_token,
        },
        headers={config.JWT_ACCESS_CSRF_HEADER_NAME: fresh_csrf_token},
    )
    assert response.status_code == 200


def test_no_token_protected_refresh(api):
    response = api.post("/protected/refresh")
    assert_auth_error(response, "MissingTokenError", "Token Error")


def test_access_token_protected_refresh(api, config: AuthXConfig, access_token: str, access_csrf_token: str):
    response = api.post(
        "/protected/refresh",
        cookies={
            config.JWT_REFRESH_COOKIE_NAME: access_token,
        },
        headers={config.JWT_REFRESH_CSRF_HEADER_NAME: access_csrf_token},
    )
    assert_auth_error(response, "RefreshTokenRequiredError", "Refresh token required")


def test_fresh_token_protected_refresh(api, config: AuthXConfig, fresh_token: str, fresh_csrf_token: str):
    response = api.post(
        "/protected/refresh",
        cookies={
            config.JWT_REFRESH_COOKIE_NAME: fresh_token,
        },
        headers={config.JWT_REFRESH_CSRF_HEADER_NAME: fresh_csrf_token},
    )
    assert_auth_error(response, "RefreshTokenRequiredError", "Refresh token required")


def test_refresh_token_protected_refresh(api, config: AuthXConfig, refresh_token: str, refresh_csrf_token: str):
    response = api.post(
        "/protected/refresh",
        cookies={
            config.JWT_REFRESH_COOKIE_NAME: refresh_token,
        },
        headers={config.JWT_REFRESH_CSRF_HEADER_NAME: refresh_csrf_token},
    )
    assert response.status_code == 200
