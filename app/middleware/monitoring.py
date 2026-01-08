import time
from typing import Awaitable, Callable

from fastapi import Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Define metrics
REQUEST_COUNT = Counter("http_requests_total", "Total number of HTTP requests", ["method", "endpoint", "status_code"])

REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency in seconds", ["method", "endpoint"])


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            process_time = time.time() - start_time

            # Record metrics
            # Use path template to avoid high cardinality (e.g., /items/{id} instead of /items/1)
            # Fallback to path if template not available
            endpoint = request.url.path
            if request.scope.get("route"):
                endpoint = request.scope["route"].path

            REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status_code=status_code).inc()

            REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(process_time)

        return response


def metrics_endpoint(request: Request) -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
