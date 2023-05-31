from unittest.mock import Mock

from fastapi import Response

from authx import AuthXDependency


class MockAuthX:
    def __init__(self):
        pass

    def create_access_token(self, uid, fresh=False, headers=None, expiry=None, data=None, audience=None):
        return "access_token"

    def create_refresh_token(self, uid, headers=None, expiry=None, data=None, audience=None):
        return "refresh_token"

    def set_access_cookies(self, token, response=None, max_age=None):
        pass

    def set_refresh_cookies(self, token, response=None, max_age=None):
        pass

    def unset_access_cookies(self, response=None):
        pass

    def unset_refresh_cookies(self, response=None):
        pass

    def unset_cookies(self, response=None):
        pass

    async def get_current_subject(self, request=None):
        return "current_subject"


async def test_authx_dependency_methods():
    authx = MockAuthX()
    request = Mock(scope={"type": "http"})
    response = Mock(spec=Response)

    authx_dependency = AuthXDependency(authx, request, response)

    assert authx_dependency.request == request
    assert authx_dependency.response == response

    access_token = authx_dependency.create_access_token("uid")
    assert access_token == "access_token"

    refresh_token = authx_dependency.create_refresh_token("uid")
    assert refresh_token == "refresh_token"

    authx_dependency.set_access_cookies("access_token")
    authx.set_access_cookies("access_token", response=response, max_age=None)

    authx_dependency.set_refresh_cookies("refresh_token")
    authx.set_refresh_cookies("refresh_token", response=response, max_age=None)

    authx_dependency.unset_access_cookies()
    authx.unset_access_cookies(response=response)

    authx_dependency.unset_refresh_cookies()
    authx.unset_refresh_cookies(response=response)

    authx_dependency.unset_cookies()
    authx.unset_cookies(response=response)

    current_subject = await authx_dependency.get_current_subject()
    assert current_subject == "current_subject"
