import datetime
import unittest

import jose.jwt
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from authx.external import MiddlewareOauth2, _get_keys


def case_1(**kwargs):
    key = "not-secret"
    audience = "audience"
    issuer = "https://example.com/"

    if "get_keys" not in kwargs:

        def _get_keys(path):
            return key

        kwargs["get_keys"] = _get_keys

    app = Starlette()

    app.add_middleware(
        MiddlewareOauth2,
        providers={
            "custom": {
                "keys": "https://example.com/tenant-id/v2.0/jwks",
                "issuer": issuer,
                "audience": audience,
            }
        },
        **kwargs,
    )
    return app, key, audience, issuer


log_message1 = 'DEBUG:authx.external.Oauth2:Trying to decode token for provider "custom", issuer "https://example.com/", audience "audience"...'
log_message2 = "DEBUG:authx.external.Oauth2:Token has expired."


def case_2(keys):
    audience = "audience"
    issuer = "https://example.com/"

    app = Starlette()
    app.add_middleware(
        MiddlewareOauth2,
        providers={
            "custom": {
                "keys": keys,
                "issuer": issuer,
                "audience": audience,
            }
        },
    )
    return app, audience, issuer


def case_3(**kwargs):
    key = "not-secret"
    calls_to_get_keys = []
    audience = "audience"
    issuer = "https://example.com/"

    def _get_keys(path):
        calls_to_get_keys.append(path)
        return key

    app = Starlette()

    kwargs["get_keys"] = _get_keys

    app.add_middleware(
        MiddlewareOauth2,
        providers={
            "custom": {
                "keys": "https://example.com/tenant-id/v2.0/jwks",
                "issuer": issuer,
                "audience": audience,
            }
        },
        **kwargs,
    )
    return app, key, audience, issuer, calls_to_get_keys


def good_claims(audience: str, issuer: str):
    return {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
        "iat": datetime.datetime.utcnow(),
        "aud": audience,
        "iss": issuer,
    }


class MiddlewareCheck:
    def __init__(self, app, storage):
        self._app = app
        self._storage = storage

    async def __call__(self, scope, receive, send):
        self._storage["scope"] = scope
        return await self._app(scope, receive, send)


class TestCase(unittest.TestCase):
    def test_no_header(self):
        app, key, audience, issuer = case_1()

        client = TestClient(app)

        with self.assertLogs(None, level="DEBUG") as cm:
            response = client.get("/")
            self.assertEqual(
                cm.output,
                [
                    'DEBUG:asyncio:Using selector: EpollSelector',
                    'DEBUG:authx.external.Oauth2:No authorization header',
                    'INFO:httpx:HTTP Request: GET http://testserver/ "HTTP/1.1 400 Bad Request"',
                ],
            )

        self.assertEqual(response.status_code, 400)

    def test_wrong_header(self):
        app, key, audience, issuer = case_1()

        client = TestClient(app)
        with self.assertLogs(None, level="DEBUG") as cm:
            response = client.get("/", headers={"authorization": "Baa "})
            self.assertEqual(
                cm.output,
                [
                    'DEBUG:asyncio:Using selector: EpollSelector',
                    'DEBUG:authx.external.Oauth2:No "Bearer" in authorization header',
                    'INFO:httpx:HTTP Request: GET http://testserver/ "HTTP/1.1 400 Bad Request"',
                ],
            )

        self.assertEqual(response.status_code, 400)

    def test_all_good(self):
        app, key, audience, issuer = case_1()

        client = TestClient(app)
        token = jose.jwt.encode(good_claims(audience, issuer), key)

        with self.assertLogs("authx.external.Oauth2", level="DEBUG") as cm:
            response = client.get("/", headers={"authorization": f"Bearer {token}"})
            self.assertEqual(cm.output, [log_message1, "DEBUG:authx.external.Oauth2:Token decoded."])

        self.assertEqual(response.status_code, 404)

    def test_keys_as_dict(self):
        key = "not-secret"
        keys = {"keys": [key]}
        app, audience, issuer = case_2(keys)

        client = TestClient(app)

        token = jose.jwt.encode(good_claims(audience, issuer), key)
        response = client.get("/", headers={"authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 404)

    def test_cors_preflight_request(self):
        app, key, audience, issuer = case_1()

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["GET", "POST"],
            allow_headers=["authorization"],
        )

        client = TestClient(app)

        response = client.options(
            "/",
            headers={
                "Access-Control-Request-Method": "GET",
                "Origin": "*",
                "Access-Control-Request-Headers": "Authorization",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_check_claims(self):
        app, key, audience, issuer = case_1()

        storage = {}
        app.add_middleware(MiddlewareCheck, storage=storage)

        client = TestClient(app)
        claims = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
            "iat": datetime.datetime.utcnow(),
            "aud": audience,
            "iss": issuer,
            "custom": "a custom claim",
        }
        token = jose.jwt.encode(claims, key)
        response = client.get("/", headers={"authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 404)

        self.assertEqual(storage["scope"]["oauth2-claims"], claims)
        self.assertEqual(storage["scope"]["oauth2-provider"], "custom")

    def test_ignore_at_hash(self):
        """Explicitly test that we ignore the ``at_hash`` of the jwt."""
        app, key, audience, issuer = case_1()

        client = TestClient(app)
        token = jose.jwt.encode(good_claims(audience, issuer), key, access_token="test_access_token")
        response = client.get("/", headers={"authorization": f"Bearer {token}"})

        self.assertEqual(response.status_code, 404)

    def test_wrong_key(self):
        app, _, audience, issuer = case_1()

        client = TestClient(app)
        token = jose.jwt.encode(good_claims(audience, issuer), "wrong-key")
        with self.assertLogs("authx.external.Oauth2", level="DEBUG") as cm:
            response = client.get("/", headers={"authorization": f"Bearer {token}"})
            self.assertEqual(len(cm.output), 2)
            self.assertEqual(cm.output[0], log_message1)
            self.assertTrue("Signature verification failed" in cm.output[1])

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": {"custom": "Signature verification failed."}})

    def test_expired(self):
        app, key, audience, issuer = case_1()

        client = TestClient(app)
        token = jose.jwt.encode(
            {
                "exp": datetime.datetime.utcnow() - datetime.timedelta(seconds=1800),
                "iat": datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
                "aud": audience,
                "iss": issuer,
            },
            key,
        )
        with self.assertLogs("authx.external.Oauth2", level="DEBUG") as cm:
            response = client.get("/", headers={"authorization": f"Bearer {token}"})
            self.assertEqual(
                cm.output,
                [
                    log_message1,
                    log_message2,
                ],
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": "Signature has expired."})

    def test_wrong_audience(self):
        app, key, audience, issuer = case_1()

        client = TestClient(app)
        token = jose.jwt.encode(
            {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
                "iat": datetime.datetime.utcnow(),
                "aud": "wrong-audience",
                "iss": issuer,
            },
            key,
        )
        with self.assertLogs("authx.external.Oauth2", level="DEBUG") as cm:
            response = client.get("/", headers={"authorization": f"Bearer {token}"})
            self.assertEqual(
                cm.output,
                [
                    log_message1,
                    "DEBUG:authx.external.Oauth2:Invalid claims",
                ],
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": {"custom": "Invalid audience"}})

    def test_wrong_issuer(self):
        app, key, audience, issuer = case_1()

        client = TestClient(app)
        token = jose.jwt.encode(
            {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
                "iat": datetime.datetime.utcnow(),
                "aud": audience,
                "iss": "wrong-issuer",
            },
            key,
        )
        with self.assertLogs("authx.external.Oauth2", level="DEBUG") as cm:
            response = client.get("/", headers={"authorization": f"Bearer {token}"})
            self.assertEqual(
                cm.output,
                [
                    log_message1,
                    "DEBUG:authx.external.Oauth2:Invalid claims",
                ],
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": {"custom": "Invalid issuer"}})

    def test_wrong_signature(self):
        app, key, audience, issuer = case_1()

        client = TestClient(app)
        token = f"{jose.jwt.encode(good_claims(audience, issuer), key)}a"

        with self.assertLogs("authx.external.Oauth2", level="DEBUG") as cm:
            response = client.get("/", headers={"authorization": f"Bearer {token}"})
            self.assertEqual(len(cm.output), 2)
            self.assertEqual(cm.output[0], log_message1)
            self.assertTrue("Signature verification failed" in cm.output[1])

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"message": {"custom": "Signature verification failed."}})

    def test_public_path(self):
        app, key, audience, issuer = case_1(public_paths={"/"})

        client = TestClient(app)
        response = client.get("/")

        self.assertEqual(response.status_code, 404)

    def test_default_get_keys(self):
        app, key, audience, issuer = case_1(public_paths={"/"}, get_keys=None)

    def test_wrong_provider(self):
        with self.assertRaises(ValueError) as e:
            MiddlewareOauth2(
                None,
                providers={
                    "custom": {
                        "keys": "https://example.com/tenant-id/v2.0/",
                        "audience": "audience",
                    }
                },
            )
        self.assertIn("\"custom\" is missing {'issuer'}.", str(e.exception))

    def test_get_keys(self):
        keys = _get_keys("https://login.microsoftonline.com/common/discovery/v2.0/keys")
        self.assertIn("keys", keys)

    @unittest.skip("This test Fails need a new test case")
    def test_wrong_configuration(self):
        with self.assertRaises(ValueError):
            case_2("http://example.com")  # missing https

    def test_key_timeout_none(self):
        app, key, audience, issuer, calls_get_keys = case_3()

        client = TestClient(app)
        token = jose.jwt.encode(good_claims(audience, issuer), key)
        response = client.get("/", headers={"authorization": f"Bearer {token}"})
        response = client.get("/", headers={"authorization": f"Bearer {token}"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(calls_get_keys), 1)

    def test_key_timeout_zero(self):
        app, key, audience, issuer, calls_get_keys = case_3(key_refresh_minutes=0)

        client = TestClient(app)
        token = jose.jwt.encode(good_claims(audience, issuer), key)
        self.callback(client, token, calls_get_keys, 1)
        self.callback(client, token, calls_get_keys, 2)

    def callback(self, client, token, calls_get_keys, additional_calls):
        result = client.get("/", headers={"authorization": f"Bearer {token}"})

        self.assertEqual(result.status_code, 404)
        self.assertEqual(len(calls_get_keys), additional_calls)

        return result

    def test_key_timeout_two(self):
        app, key, audience, issuer, calls_get_keys = case_3(key_refresh_minutes=2)

        client = TestClient(app)
        token = jose.jwt.encode(good_claims(audience, issuer), key)
        response = client.get("/", headers={"authorization": f"Bearer {token}"})
        response = client.get("/", headers={"authorization": f"Bearer {token}"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(calls_get_keys), 1)

    def test_key_refresh_dict(self):
        app, key, audience, issuer, calls_get_keys = case_3(key_refresh_minutes={"custom": 0})

        client = TestClient(app)
        token = jose.jwt.encode(good_claims(audience, issuer), key)
        response = client.get("/", headers={"authorization": f"Bearer {token}"})
        response = client.get("/", headers={"authorization": f"Bearer {token}"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(calls_get_keys), 2)

    def test_websocket_ok(self):
        app, key, audience, issuer = case_1()

        @app.websocket_route("/ws")
        async def websocket_endpoint(websocket):
            await websocket.accept()
            await websocket.send_text("Hello, world!")
            await websocket.close()

        client = TestClient(app)
        token = jose.jwt.encode(good_claims(audience, issuer), key)

        with client.websocket_connect("/ws", headers={"authorization": f"Bearer {token}"}) as websocket:
            data = websocket.receive_text()
            self.assertEqual(data, "Hello, world!")

    def test_websocket_not_ok(self):
        app, key, audience, issuer = case_1()

        @app.websocket_route("/ws")
        async def websocket_endpoint(websocket):
            await websocket.accept()
            await websocket.send_text("Hello, world!")
            await websocket.close()

        client = TestClient(app)
        invalid_key = f"{key}a"
        token = jose.jwt.encode(good_claims(audience, issuer), invalid_key)

        with self.assertRaises(WebSocketDisconnect):
            with client.websocket_connect("/ws", headers={"authorization": f"Bearer {token}"}):
                pass
