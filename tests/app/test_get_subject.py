def assert_auth_error(response, error_type: str, message: str):
    assert response.status_code == 401
    assert response.json() == {"message": message, "error_type": error_type}


def test_no_authorization_get_subject(api):
    response = api.get("/entity/subject")
    assert_auth_error(response, "MissingTokenError", "Token Error")


def test_get_subject_access_token(api, access_token: str):
    response = api.get("/entity/subject", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


def test_get_subject_refresh_token(api, refresh_token: str):
    response = api.get("/entity/subject", headers={"Authorization": f"Bearer {refresh_token}"})
    assert_auth_error(response, "AccessTokenRequiredError", "Access token required")


def test_get_subject(api, access_token: str):
    response = api.get("/entity/subject", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["subject"]["uid"] == "test"
    assert response.json()["subject"]["email"] == "test@test.com"


def test_get_subject_resources(api, access_token: str):
    response = _test_get_subject_resources(api, access_token, 0)
    response = api.post(
        "/entity/resources",
        json={"subject": "test", "resource": "A dummy resources"},
    )

    response = _test_get_subject_resources(api, access_token, 1)
    response = api.post(
        "/entity/resources",
        json={"subject": "foo", "resource": "A dummy resources"},
    )

    response = _test_get_subject_resources(api, access_token, 1)
    response = api.get("/entity/resources")
    assert response.status_code == 200
    assert len(response.json()["resources"]) == 2


def _test_get_subject_resources(api, access_token, argument):
    result = api.get(
        "/entity/subject/resources",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert result.status_code == 200
    assert len(result.json()["resources"]) == argument

    return result
