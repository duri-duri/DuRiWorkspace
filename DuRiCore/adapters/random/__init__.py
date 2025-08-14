from DuRiCore.trace import emit_trace
"""
Random number generator adapters implementing RandomPort interface.
"""
from .system_random import SystemRandom, ControlledRandom
__all__ = ['SystemRandom', 'ControlledRandom']