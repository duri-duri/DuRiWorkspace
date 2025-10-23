# ops/observability/otel_init.py
import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)

DEFAULT_ENDPOINT = "http://localhost:4318/v1/traces"

_INITIALIZED = False


def init_tracing(
    service_name: str = "duri-core", endpoint: Optional[str] = None
) -> None:
    """
    Idempotent. Safe to call multiple times.
    """
    global _INITIALIZED
    if _INITIALIZED:
        return

    endpoint = endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", DEFAULT_ENDPOINT)

    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))

    # Docker 없이 ConsoleExporter로 즉시 시작
    print(f"🚀 ConsoleExporter로 시작 (Docker 없음)")
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
    _INITIALIZED = True


def get_tracer(instrumentation: str = "duri") -> trace.Tracer:
    init_tracing()  # ensure provider
    return trace.get_tracer(instrumentation)
