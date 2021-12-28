from unittest import TestCase

from starlette.config import environ
from starlette.datastructures import URL
from starlette.testclient import TestClient


class Test(TestCase):
    @classmethod
    def setUpClass(cls):
        environ["SECRET_KEY"] = "secretKey"
        environ[
            "SERVER_METADATA_URL"
        ] = "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
        environ["CLIENT_ID"] = "00000000-0000-0000-0000-000000000000"
        environ[
            "CLIENT_SECRET"
        ] = "0000000000000000000000000000000000000000000000000000000000000000"

        import example.app

        app = example.app.app

        cls.client = TestClient(app)

    def test_redirects(self):
        response = self.client.get("/", allow_redirects=False)

        self.assertEqual(302, response.status_code)
        url = URL(response.headers["Location"])
        self.assertEqual(url.scheme, "https")
        self.assertEqual(url.netloc, "login.microsoftonline.com")
        self.assertEqual(url.path, "/common/oauth2/v2.0/authorize")
        self.assertIn("redirect_uri=http%3A%2F%2Ftestserver%2Fauthorized", url.query)
        self.assertIn("client_id=00000000-0000-0000-0000-000000000000", url.query)
        self.assertIn("scope=openid+email+profile", url.query)
