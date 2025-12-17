"""
otel_exporter.py — OpenTelemetry integration for A-LOG.
This module initializes a tracer and exports A-LOG events as spans.
"""

import json
from typing import Dict, Any, Optional

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
except Exception:  # pragma: no cover - allow import without OTel installed
    trace = None  # type: ignore
    SERVICE_NAME = "service.name"  # fallback key
    Resource = None  # type: ignore
    TracerProvider = None  # type: ignore
    BatchSpanProcessor = None  # type: ignore
    OTLPSpanExporter = None  # type: ignore


class OTelExporter:
    """
    Initializes and manages an OpenTelemetry tracer.
    Converts A-LOG events into OpenTelemetry spans and sends them to a collector.
    """

    def __init__(self, service_name: str = "A-LOG", endpoint: str = "http://localhost:4317"):
        if trace is None or TracerProvider is None:
            self.tracer = None
            return

        # Resource metadata that identifies this service in the collector
        resource = Resource.create({SERVICE_NAME: service_name}) if Resource else None

        # Set up provider, exporter, and processor
        provider = TracerProvider(resource=resource) if resource else TracerProvider()
        # Use gRPC exporter matching Jaeger all-in-one default port 4317
        exporter = OTLPSpanExporter(endpoint=endpoint)  # type: ignore[arg-type]
        processor = BatchSpanProcessor(exporter)  # type: ignore[arg-type]
        provider.add_span_processor(processor)

        # Set this as the global tracer
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(service_name)

    def emit_span(self, surface: str, agent: str, event: Dict[str, Any], context: Optional[object] = None) -> None:
        """
        Emit a span for a given A-LOG event.

        Args:
            surface: The log surface ('operational', 'cognitive', or 'contextual')
            agent: The agent name
            event: The structured event dictionary containing event-specific fields
            context: Optional OpenTelemetry context for span propagation

        Note:
            - Skips None values to keep spans clean
            - Complex objects are serialized to strings
            - Attributes that fail to serialize are converted using repr()
        """
        if self.tracer is None:
            return

        span_name = f"{agent}.{surface}"
        # start span within provided context (to keep spans on same trace)
        with self.tracer.start_as_current_span(span_name, context=context) as span:  # type: ignore[arg-type]
            # Set surface and agent as primary attributes
            span.set_attribute("surface", surface)
            span.set_attribute("agent", agent)

            # Add event-specific attributes
            for key, value in event.items():
                # Skip None values to keep spans clean
                if value is None:
                    continue

                try:
                    # OpenTelemetry supports str, int, float, bool, and sequences of these
                    if isinstance(value, (str, int, float, bool)):
                        span.set_attribute(key, value)
                    elif isinstance(value, (list, tuple)):
                        # Convert sequences to strings if they contain complex types
                        span.set_attribute(key, str(value))
                    elif isinstance(value, dict):
                        # For dictionaries, convert to JSON string
                        span.set_attribute(key, json.dumps(value))
                    else:
                        # For other types, convert to string
                        span.set_attribute(key, str(value))
                except Exception as e:
                    # Last resort: use repr() for problematic values
                    try:
                        span.set_attribute(key, repr(value))
                    except Exception:
                        # If even repr() fails, log the key with an error message
                        span.set_attribute(key, f"<error serializing value: {type(value).__name__}>")

