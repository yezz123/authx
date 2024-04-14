# Metrics Using Prometheus

!!! warning
     You need to install dependencies for the middleware you want to use

Metrics collection with Prometheus relies on the pull model, meaning that Prometheus is responsible for getting metrics (scraping) from the services that it monitors. This is diametrically opposed from other tools like Graphite, which are passively waiting on clients to push their metrics to a known server.

The `MetricsMiddleware` class is a middleware that collects Prometheus metrics for each request in a FastAPI application. It inherits from `BaseHTTPMiddleware` class provided by Starlette.

```python
class MetricsMiddleware(BaseHTTPMiddleware):

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
        ...
```

## Exposing and scraping metrics

Clients have only one responsibility: make their metrics available for a Prometheus server to scrape. This is done by exposing an HTTP endpoint, usually /metrics, which returns the full list of metrics (with label sets) and their values. This endpoint is very cheap to call as it simply outputs the current value of each metric, without doing any calculation.

![Prometheus scraping](https://blog.pvincent.io/images/prometheus-series/prometheus-service-scrape.png)

On the Prometheus server side, each target (statically defined, or dynamically discovered) is scraped at a regular interval (scrape interval). Each scrape reads the /metrics to get the current state of the client metrics, and persists the values in the Prometheus time-series database.

#### Initialization

- `app`: A `FastAPI` instance representing the FastAPI application.
- `prefix`: A string specifying the prefix for the Prometheus metrics. Default value is "authx_".
- `buckets`: A tuple of float values representing the histogram buckets for request durations. Default buckets are (0.002, 0.05, 0.1, +Inf).

#### Methods

- `dispatch`: This method is called for each request and records the request method, path, and status. It measures the time taken to process the request and updates the corresponding Prometheus metrics.
  - Parameters:
    - `request`: A `Request` instance representing the incoming request.
    - `call_next`: A callable function representing the next middleware or request handler to be called in the pipeline.
  - Returns:
    - `response`: A `Response` instance representing the response to be sent back to the client.

#### Functions

- `request_count`: A cached function that returns a Prometheus Counter metric for tracking the total number of requests.
  - Parameters:
    - `prefix`: A string specifying the prefix for the Prometheus metric.
  - Returns:
    - `Counter`: A Prometheus Counter metric object.

- `request_time`: A cached function that returns a Prometheus Histogram metric for tracking the duration of requests.
  - Parameters:
    - `prefix`: A string specifying the prefix for the Prometheus metric.
    - `buckets`: A tuple of float values representing the histogram buckets for request durations.
  - Returns:
    - `Histogram`: A Prometheus Histogram metric object.

- `get_registry`: A cached function that returns the Prometheus CollectorRegistry.
  - Returns:
    - `CollectorRegistry`: A Prometheus CollectorRegistry object.

- `get_metrics`: A request handler function that returns the Prometheus metrics.
  - Parameters:
    - `_`: A `Request` instance representing the incoming request (not used).
  - Returns:
    - `Response`: A `Response` instance containing the Prometheus metrics in the Prometheus text exposition format.

## How to install

Make sure to have the necessary dependencies installed (e.g., `prometheus_client`, `fastapi`, `starlette`).

<div class="termy">

```console
$ pip install authx_extra

---> 100%
```

</div>

## Implementation in FastAPI applications

Thats Work by adding a Middleware to your FastAPI application, work on collecting prometheus metrics for each request, and then to handle that we need a function `get_metrics` work on handling exposing the prometheus metrics into `/metrics` endpoint.

```python
from fastapi import FastAPI
from authx_extra.metrics import MetricsMiddleware, get_metrics

app = FastAPI()
app.add_middleware(MetricsMiddleware)
app.add_route("/metrics", get_metrics)
```
