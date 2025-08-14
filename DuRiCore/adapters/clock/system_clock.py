from DuRiCore.trace import emit_trace
"""
System clock adapter implementing ClockPort interface.
Provides real system time for production use.
"""
from datetime import datetime
import time
from core.ports import ClockPort

class SystemClock(ClockPort):
    """
    System clock implementation using real system time.
    Suitable for production environments.
    """

    def now(self) -> datetime:
        """Get current UTC timestamp"""
        return datetime.utcnow()

    def time(self) -> float:
        """Get current time as float (for performance measurements)"""
        return time.time()

class MockClock(ClockPort):
    """
    Mock clock for testing purposes.
    Allows time manipulation and control.
    """

    def __init__(self, initial_time: float=1000000.0):
        """
        Initialize mock clock with initial time.
        
        Args:
            initial_time: Starting time as float (Unix timestamp)
        """
        self._current_time = initial_time
        self._time_increment = 0.001

    def now(self) -> datetime:
        """Get current mock timestamp"""
        return datetime.fromtimestamp(self._current_time)

    def time(self) -> float:
        """Get current mock time as float"""
        return self._current_time

    def advance(self, seconds: float) -> None:
        """Advance time by specified seconds"""
        self._current_time += seconds

    def set_time(self, timestamp: float) -> None:
        """Set time to specific timestamp"""
        self._current_time = timestamp

    def set_time_increment(self, increment: float) -> None:
        """Set time increment for each call"""
        self._time_increment = increment

    def tick(self) -> None:
        """Advance time by one increment"""
        self._current_time += self._time_increment