from authx.config import AuthXConfig


def assert_revoked_token_error(response):
    assert response.status_code == 401
    assert response.json() == {
        "message": "Invalid token",
        "error_type": "RevokedTokenError",
    }


def test_blocklist_access_token(api, access_token: str):
    # Check token not in list
    blocklist = api.get("/blocklist").json()["blocklist"]
    assert access_token not in blocklist

    # Check token works
    response = api.post("/protected/access", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

    # Check Block token
    response = api.post("/token/block", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

    # Check token in blocklist
    blocklist = api.get("/blocklist").json()["blocklist"]
    assert access_token in blocklist

    # Check token no longer works
    response = api.post("/protected/access", headers={"Authorization": f"Bearer {access_token}"})
    assert_revoked_token_error(response)


def test_blocklist_refresh_token(api, config: AuthXConfig, refresh_token: str, refresh_csrf_token: str):
    blocklist = api.get("/blocklist").json()["blocklist"]
    assert refresh_token not in blocklist

    response = api.post(
        "/protected/refresh",
        cookies={
            config.JWT_REFRESH_COOKIE_NAME: refresh_token,
        },
        headers={config.JWT_REFRESH_CSRF_HEADER_NAME: refresh_csrf_token},
    )
    assert response.status_code == 200

    response = api.post("/token/block", headers={"Authorization": f"Bearer {refresh_token}"})
    assert response.status_code == 200

    blocklist = api.get("/blocklist").json()["blocklist"]
    assert refresh_token in blocklist

    response = api.post(
        "/protected/refresh",
        cookies={
            config.JWT_REFRESH_COOKIE_NAME: refresh_token,
        },
        headers={config.JWT_REFRESH_CSRF_HEADER_NAME: refresh_csrf_token},
    )
    assert_revoked_token_error(response)
