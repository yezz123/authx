import functools
import os
import time
import typing

import prometheus_client
from fastapi import FastAPI, Request
from prometheus_client.multiprocess import MultiProcessCollector
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Metrics middleware collecting prometheus metrics for each request."""

    def __init__(
        self,
        app: FastAPI,
        prefix: str = "authx_",
        buckets: typing.Tuple[float, ...] = (
            0.002,
            0.05,
            0.1,
            prometheus_client.utils.INF,
        ),
    ) -> None:
        """Initialize a new MetricsMiddleware instance."""
        super().__init__(app)
        self.request_count = request_count(prefix)
        self.request_time = request_time(prefix, buckets)

    async def dispatch(self, request: Request, call_next: typing.Callable):
        """Record request method, path and status when dispatching."""
        method = request.method
        path = request.url.path
        status = 500
        begin = time.time()
        try:
            response = await call_next(request)
            status = response.status_code
        finally:
            # track urls w/ params grouped, eg. /items/123 -> /items/{id}
            router = request.scope.get("router")
            endpoint = request.scope.get("endpoint")
            if router and endpoint:
                for route in router.routes:
                    route_app = getattr(route, "app", None)
                    route_endpoint = getattr(route, "endpoint", None)
                    if endpoint in (route_app, route_endpoint):
                        path = route.path
                        break
            end = time.time()
            labels = [method, path, status]
            self.request_count.labels(*labels).inc()
            self.request_time.labels(*labels).observe(end - begin)
        return response


@functools.lru_cache()
def request_count(prefix: str) -> prometheus_client.Counter:
    """Return request count metric for the app prefix (cached/singleton)."""
    return prometheus_client.Counter(
        f"{prefix}requests_total",
        "Total HTTP requests",
        ("method", "path", "status"),
        registry=get_registry(),
    )


@functools.lru_cache()
def request_time(
    prefix: str, buckets: typing.Tuple[float, ...]
) -> prometheus_client.Histogram:
    """Return request time metric for the app prefix (cached/singleton)."""
    return prometheus_client.Histogram(
        f"{prefix}request_duration_seconds",
        "HTTP request duration in seconds",
        ("method", "path", "status"),
        buckets=buckets,
        registry=get_registry(),
    )


@functools.lru_cache()
def get_registry() -> prometheus_client.registry.CollectorRegistry:
    """Get the metrics collector registry."""
    registry = prometheus_client.CollectorRegistry()
    if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
        MultiProcessCollector(registry)
    return registry


def get_metrics(_: Request) -> Response:
    """Handler exposing the prometheus metrics."""
    metrics = prometheus_client.generate_latest(get_registry())
    return Response(metrics, media_type=prometheus_client.CONTENT_TYPE_LATEST)
