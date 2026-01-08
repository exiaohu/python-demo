from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings
from app.core.logger import logger


def setup_opentelemetry(app: FastAPI) -> None:
    if not settings.OTEL_ENABLED:
        return

    logger.info("Setting up OpenTelemetry...")

    resource = Resource.create(
        attributes={
            "service.name": settings.OTEL_SERVICE_NAME,
            "service.version": settings.VERSION,
            "deployment.environment": settings.SENTRY_ENVIRONMENT,
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    otlp_exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    logger.info("OpenTelemetry setup complete.")
