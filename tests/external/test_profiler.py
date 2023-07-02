import json
import os
import sys
from io import StringIO

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from authx.external import ProfilerMiddleware


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
            profiler_kwargs["server_app"] = app
        app.add_middleware(ProfilerMiddleware, **profiler_kwargs)

        @app.get("/test")
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

        request_path = "/tests/external"
        client.get(request_path)

        sys.stdout = temp_stdout
        assert f"Path: {request_path}" in stdout_redirect.fp.getvalue()

    def test_profiler_export_to_html(self, test_middleware):
        full_path = f"{os.getcwd()}/tests/external/authx_profiling_results.html"

        with TestClient(
            test_middleware(
                profiler_output_type="html",
                is_print_each_request=False,
                html_file_name=full_path,
            )
        ) as client:
            # request
            request_path = "/tests/external"
            client.get(request_path)

        with open(full_path) as f:
            assert "profiler.py" in f.read()

    def test_profiler_export_to_json(self, test_middleware):
        full_path = f"{os.getcwd()}/tests/external/authx_profiling_results.json"

        with TestClient(
            test_middleware(
                profiler_output_type="json",
                is_print_each_request=False,
                json_file_name=full_path,
            )
        ) as client:
            # request
            request_path = "/tests/external"
            client.get(request_path)

    def test_normal_request(self, client):
        response = client.get("/test")
        assert response.status_code == 422

    def test_profiler_output_text(self, test_middleware):
        stdout_redirect.fp = StringIO()
        temp_stdout, sys.stdout = sys.stdout, stdout_redirect

        with TestClient(
            test_middleware(
                is_print_each_request=True,
                profiler_output_type="text",
            )
        ) as client:
            client.get("/test")

        sys.stdout = temp_stdout
        output_text = stdout_redirect.fp.getvalue()

        assert "Method: GET" in output_text
        assert "Path: /test" in output_text
        assert "Duration: " in output_text

    def test_profiler_output_html(self, test_middleware):
        full_path = f"{os.getcwd()}/tests/external/authx_profiling_results.html"

        with TestClient(
            test_middleware(
                profiler_output_type="html",
                is_print_each_request=False,
                html_file_name=full_path,
            )
        ) as client:
            client.get("/test")

        with open(full_path) as f:
            html_content = f.read()
            assert "profiler.py" in html_content

    def test_profiler_output_json(self, test_middleware):
        full_path = f"{os.getcwd()}/tests/external/authx_profiling_results.json"

        with TestClient(
            test_middleware(
                profiler_output_type="json",
                is_print_each_request=False,
                json_file_name=full_path,
            )
        ) as client:
            client.get("/test")

        with open(full_path) as f:
            json_data = json.load(f)
            assert isinstance(json_data, dict)
