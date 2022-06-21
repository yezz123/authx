import sys
from io import StringIO

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from authx.middleware.profiler import ProfilerMiddleware


class ConsoleOutputRedirect:
    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


stdout_redirect = ConsoleOutputRedirect(sys.stdout)


@pytest.fixture(name="test_middleware")
def test_middleware():
    def _test_middleware(**profiler_kwargs):
        app = FastAPI()
        if profiler_kwargs.get("profiler_output_type") != "text":
            profiler_kwargs.update({"server_app": app})
        app.add_middleware(ProfilerMiddleware, **profiler_kwargs)

        @app.route("/test")
        async def normal_request(request):
            return JSONResponse({"retMsg": "Normal Request test Success!"})

        return app

    return _test_middleware


class TestProfilerMiddleware:
    @pytest.fixture
    def client(self, test_middleware):
        return TestClient(test_middleware())

    def test_profiler_print_at_console(self, client):
        stdout_redirect.fp = StringIO()
        temp_stdout, sys.stdout = sys.stdout, stdout_redirect

        request_path = "/tests/middleware"
        client.get(request_path)

        sys.stdout = temp_stdout
        assert f"Path: {request_path}" in stdout_redirect.fp.getvalue()
