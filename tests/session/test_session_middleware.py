import time
from unittest.mock import Mock

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from starlette.testclient import TestClient

from authx._internal import MemoryIO
from authx.external import SessionMiddleware


def test_create_session_id_and_store():
    async def test_route(request):
        return PlainTextResponse("Hello, world!")

    routes = [Route("/", endpoint=test_route)]
    app = Starlette(routes=routes)

    app.add_middleware(
        SessionMiddleware,
        secret_key='test-secret',
        store=MemoryIO(),
        http_only=True,
        max_age=3600,
        secure=True,
        session_cookie="sid",
    )
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, world!"
    assert "sid" in response.cookies


def test_session_counter_increment():
    async def test_route(request):
        session = request.state.session.get_session()
        if "test_counter" not in session:
            session["test_counter"] = 0

        session["test_counter"] += 1

        return PlainTextResponse(f"Counter: {session['test_counter']}")

    routes = [Route("/", endpoint=test_route)]

    app = Starlette(routes=routes)
    is_cookie_secure = False
    app.add_middleware(
        SessionMiddleware,
        secret_key='test-secret',
        store=MemoryIO(),
        http_only=True,
        max_age=3600,
        secure=is_cookie_secure,
        session_cookie="sid",
    )
    client = TestClient(app)

    # First request
    response = client.get("/")
    assert response.status_code == 200
    assert "Counter: 1" in response.text

    # Second request
    response = client.get("/")
    assert response.status_code == 200
    assert "Counter: 2" in response.text

    # Third request
    response = client.get("/")
    assert response.status_code == 200
    assert "Counter: 3" in response.text


def test_session_cookie_expiry():
    async def test_route(request):
        session = request.state.session.get_session()

        if "test_counter" not in session:
            session["test_counter"] = 0

        session["test_counter"] += 1

        return PlainTextResponse(f"Counter: {session['test_counter']}")

    routes = [Route("/", endpoint=test_route)]

    app = Starlette(routes=routes)
    is_cookie_secure = False
    app.add_middleware(
        SessionMiddleware,
        secret_key='test-secret',
        store=MemoryIO(),
        http_only=True,
        max_age=1,
        secure=is_cookie_secure,
        session_cookie="sid",
    )
    client = TestClient(app)

    # First request
    response = client.get("/")
    assert response.status_code == 200
    assert "Counter: 1" in response.text

    # Wait for more than max_age seconds
    time.sleep(2)

    # Second request after expiry
    response = client.get("/")
    assert response.status_code == 200
    assert "Counter: 1" in response.text  # Counter should reset to 1


def test_session_cookie_not_persisted_with_secure_option():
    app = Starlette()
    is_cookie_secure = True
    app.add_middleware(
        SessionMiddleware,
        secret_key='test-secret',
        store=MemoryIO(),
        http_only=True,
        max_age=3600,
        secure=is_cookie_secure,
        session_cookie="sid",
    )

    @app.route("/")
    async def test_route(request):
        session = request.state.session.get_session()
        if "test_counter" not in session:
            session["test_counter"] = 0

        session["test_counter"] += 1

        return PlainTextResponse(f"Counter: {session['test_counter']}")

    client = TestClient(app)

    # First request
    response = client.get("/")
    assert response.status_code == 200
    assert "Counter: 1" in response.text

    # Second request
    response = client.get("/")
    assert response.status_code == 200
    # Since the secure option is set, the cookie should not be persisted
    # and the counter should not increment.
    assert "Counter: 1" in response.text


def test_check_httponly_flag_in_cookie():
    async def test_route(request):
        session = request.state.session.get_session()
        if "test_counter" not in session:
            session["test_counter"] = 0

        session["test_counter"] += 1

        return PlainTextResponse(f"Counter: {session['test_counter']}")

    app = Starlette()
    app.add_route("/", test_route)

    is_cookie_secure = False
    is_http_only = True
    app.add_middleware(
        SessionMiddleware,
        secret_key='test-secret',
        store=MemoryIO(),
        http_only=is_http_only,
        max_age=3600,
        secure=is_cookie_secure,
        session_cookie="sid",
    )

    client = TestClient(app)

    # First request
    response = client.get("/")
    assert 'HttpOnly' in response.headers['Set-Cookie']


def test_check_no_httponly_flag_in_cookie():
    async def test_route(request):
        session = request.state.session.get_session()
        if "test_counter" not in session:
            session["test_counter"] = 0

        session["test_counter"] += 1

        return PlainTextResponse(f"Counter: {session['test_counter']}")

    app = Starlette()
    app.add_route("/", test_route)

    is_cookie_secure = False
    is_http_only = False
    app.add_middleware(
        SessionMiddleware,
        secret_key='test-secret',
        store=MemoryIO(),
        http_only=is_http_only,
        max_age=3600,
        secure=is_cookie_secure,
        session_cookie="sid",
    )

    client = TestClient(app)

    # First request
    response = client.get("/")
    assert 'HttpOnly' not in response.headers['Set-Cookie']


@pytest.mark.asyncio
async def test_dispatch_should_skip_session_management_with_skip_header():
    app = Mock(return_value=Response("OK"))
    middleware = SessionMiddleware(
        app=app, secret_key="test", skip_session_header={"header_name": "X-APITEST-Skip", "header_value": "skip"}
    )

    headers = [(b"x-APITEST-skip", b"skip")]
    request = Request(scope={"type": "http", "headers": headers}, receive=None)

    class MockResponse:
        def __init__(self):
            self.headers = {}

    emulated_response = MockResponse()

    async def call_next(request):
        return emulated_response

    response = await middleware.dispatch(request, call_next)
    print(f"res:{response}")
    assert not hasattr(request.state, 'session')


@pytest.mark.asyncio
async def test_dispatch_should_not_skip_session_management_without_skip_heade1r():
    app = Mock(return_value=Response("OK"))
    middleware = SessionMiddleware(
        app=app, secret_key="test", skip_session_header={"header_name": "X-APITEST-Skip", "header_value": "skip"}
    )

    headers = [(b"ignore", b"ignore")]
    request = Request(scope={"type": "http", "headers": headers}, receive=None)

    class MockResponse:
        def __init__(self):
            self.headers = {}

    emulated_response = MockResponse()

    async def call_next(request):
        return emulated_response

    response = await middleware.dispatch(request, call_next)
    print(f"res:{response}")
    assert hasattr(request.state, 'session')
