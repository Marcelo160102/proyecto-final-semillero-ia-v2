import socket

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.langchain import LangChainInstrumentor

from app.config import obtener_config


def _phoenix_disponible(host: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        return sock.connect_ex((host, port)) == 0
    finally:
        sock.close()


def setup_phoenix():
    config = obtener_config()
    if not _phoenix_disponible(config.phoenix_host, config.phoenix_port):
        import logging

        logging.warning(
            "Phoenix no disponible en %s:%s, omitiendo telemetria",
            config.phoenix_host,
            config.phoenix_port,
        )
        return

    endpoint = f"http://{config.phoenix_host}:{config.phoenix_port}/v1/traces"
    provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint=endpoint, timeout=2)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    LangChainInstrumentor().instrument()