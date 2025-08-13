from DuRiCore.trace import emit_trace
"""
Metrics adapters implementing MetricsPort interface.
"""
from .in_memory_metrics import InMemoryMetrics
__all__ = ['InMemoryMetrics']