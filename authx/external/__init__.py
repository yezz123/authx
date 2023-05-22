try:
    from authx.external.metrics import MetricsMiddleware, get_metrics, request_count, request_time
except ImportError as e:
    raise ImportError("Missing dependency: pip install authx[metrics]") from e

try:
    from authx.external.Oauth2 import MiddlewareOauth2
except ImportError as e:
    raise ImportError("Missing dependency: pip install authx[oauth2]") from e

try:
    from authx.external.profiler import ProfilerMiddleware
except ImportError as e:
    raise ImportError("Missing dependency: pip install authx[profiler]") from e


__all__ = "MetricsMiddleware", "MiddlewareOauth2", "ProfilerMiddleware", "get_metrics", "request_count", "request_time"
