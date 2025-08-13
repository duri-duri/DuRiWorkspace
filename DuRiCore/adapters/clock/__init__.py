from DuRiCore.trace import emit_trace
"""
Clock adapters implementing ClockPort interface.
"""
from .system_clock import SystemClock, MockClock
__all__ = ['SystemClock', 'MockClock']