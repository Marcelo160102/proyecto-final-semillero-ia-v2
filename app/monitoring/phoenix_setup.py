from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.langchain import LangChainInstrumentor

from app.config.config import obtener_config


# ADVERTENCIA: LangChainInstrumentor captura input/output completo del LLM
# (preguntas, respuestas y argumentos de tools como proveedor/monto).
# No usar en produccion con datos reales sin implementar filtro de campos sensibles.
def setup_phoenix():
    config = obtener_config()
    endpoint = f"http://{config.phoenix_host}:{config.phoenix_port}/v1/traces"
    provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint=endpoint, timeout=2)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    LangChainInstrumentor().instrument()
