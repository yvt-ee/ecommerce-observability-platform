"""
OpenTelemetry setup: traces + metrics, exported via OTLP/gRPC to the OTEL
Collector. This is the *observability* pipeline and is intentionally kept
separate from the business data pipeline (FastAPI -> Databricks/PySpark ->
Delta tables). Nothing here writes business data, and nothing in the data
pipeline emits telemetry.

If the collector isn't reachable (e.g. running the API standalone without
`docker compose up`), the OTLP exporters just fail to connect on a
background thread -- requests are unaffected, so this is safe to leave
enabled by default.
"""
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import settings

_tracer = trace.get_tracer(settings.otel_service_name)


def get_tracer() -> trace.Tracer:
    """Tracer used for custom, business-meaning spans (create_order, etc.)."""
    return _tracer


def setup_telemetry(app: FastAPI) -> None:
    """Wire up tracing + metrics and attach the request-metrics middleware.

    Call this once, right after the FastAPI app is created in main.py.
    """
    if not settings.otel_enabled:
        return

    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.namespace": "ecommerce-data-platform",
            "deployment.environment": settings.environment,
        }
    )

    # --- Traces: one span per HTTP request (automatic) + custom spans (manual) ---
    tracer_provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)

    # --- Metrics: request count, duration, and errors, exported periodically ---
    metric_exporter = OTLPMetricExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
    metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=5000)
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Automatic instrumentation: creates a span per request with route,
    # method, status code, and records exceptions on the span automatically.
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider, meter_provider=meter_provider)

    # Explicit, hand-named metrics. Auto-instrumentation already emits HTTP
    # metrics too, but these give the Grafana dashboard predictable names to
    # query against instead of depending on a specific library version's
    # semantic-convention naming.
    meter = metrics.get_meter(settings.otel_service_name)
    request_counter = meter.create_counter(
        name="http_server_requests",
        unit="1",
        description="Total number of HTTP requests handled",
    )
    error_counter = meter.create_counter(
        name="http_server_errors",
        unit="1",
        description="Total number of HTTP requests that resulted in a 5xx response or an exception",
    )
    duration_histogram = meter.create_histogram(
        name="http_server_duration",
        unit="s",
        description="HTTP request duration in seconds",
    )

    @app.middleware("http")
    async def record_request_metrics(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # All routes in this API are static (no /orders/{id} style paths),
        # so request.url.path is already a safe, low-cardinality label.
        route = request.url.path
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.perf_counter() - start
            attributes = {
                "http.method": request.method,
                "http.route": route,
                "http.status_code": status_code,
            }
            request_counter.add(1, attributes)
            duration_histogram.record(duration, attributes)
            if status_code >= 500:
                error_counter.add(1, attributes)
