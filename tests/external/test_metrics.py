import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
from prometheus_client.parser import text_string_to_metric_families

from authx.external import MetricsMiddleware, get_metrics


@pytest.fixture(autouse=True)
def env(monkeypatch):
    """Run tests with 'PROMETHEUS_MULTIPROC_DIR' in the env by default."""
    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", "/tmp")


@pytest.fixture
def client():
    """Return a test client for a simple FastAPI instance with metrics."""
    app = FastAPI()
    app.add_middleware(MetricsMiddleware)
    app.add_route("/metrics", get_metrics)
    app.add_route("/foo", lambda _: Response("bar"))
    return TestClient(app)


def test_metrics_keys(client):
    """Test that all expected metric families are exported."""
    metrics = scrape_metrics(client)
    assert set(metrics.keys()) == {
        "authx_request_duration_seconds",
        "authx_requests",
    }


def test_metrics_values(client):
    """Test that GET /foo is recorded via metrics."""
    assert client.get("/foo")
    metrics = scrape_metrics(client)

    request_durations = metrics["authx_request_duration_seconds"]
    assert "method=GET,path=/foo,status=200" in request_durations


def scrape_metrics(client):
    """GET /metrics response and return it parsed for asserting."""
    response = client.get("/metrics")
    metrics = {}
    for metric in text_string_to_metric_families(response.text):
        # skip standard python metrics
        if not metric.name.startswith("authx_"):
            continue
        # "dictify" metrics for simple comparison in tests
        metrics[metric.name] = labels = {}
        for sample in metric.samples:
            label = ",".join(f"{k}={v}" for k, v in sorted(sample.labels.items()))
            labels[label] = sample.value
    return metrics
