from DuRiCore.trace import emit_trace
"""
Mock validator adapter implementing ValidatorPort interface.
Provides controlled validation behavior for testing scenarios.
"""
import asyncio
import random
from typing import Dict, Any, Optional
from datetime import datetime
from core.ports import ValidatorPort, ValidationResult
from core.errors import ValidationError, TransientError, SystemError

class MockValidator(ValidatorPort):
    """
    Mock validator for testing purposes.
    Simulates various validation scenarios with configurable behavior.
    """

    def __init__(self, success_rate: float=0.95, base_latency_ms: float=10.0, latency_variance_ms: float=5.0, failure_patterns: Optional[Dict[str, float]]=None):
        """
        Initialize mock validator with configurable behavior.
        
        Args:
            success_rate: Probability of successful validation (0.0 to 1.0)
            base_latency_ms: Base response time in milliseconds
            latency_variance_ms: Random variance in response time
            failure_patterns: Dict of error types and their probabilities
        """
        self.success_rate = max(0.0, min(1.0, success_rate))
        self.base_latency_ms = base_latency_ms
        self.latency_variance_ms = latency_variance_ms
        self.failure_patterns = failure_patterns or {'validation_error': 0.7, 'timeout_error': 0.2, 'system_error': 0.1}
        self._request_counter = 0
        self._random = random.Random()

    def seed(self, seed_value: int) -> None:
        """Set random seed for reproducible behavior"""
        self._random.seed(seed_value)

    async def validate(self, request_id: int, data: Dict[str, Any]) -> ValidationResult:
        """Simulate validation with configurable behavior"""
        self._request_counter += 1
        if data.get('value') == 'timeout':
            raise TransientError('simulated timeout')
        if data.get('value') == 'boom':
            raise SystemError('simulated system error')
        if isinstance(data.get('value'), int) and data['value'] < 0:
            raise ValidationError('negative not allowed')
        latency_ms = self.base_latency_ms + self._random.uniform(-self.latency_variance_ms, self.latency_variance_ms)
        latency_ms = max(0.1, latency_ms)
        await asyncio.sleep(latency_ms / 1000.0)
        is_success = self._random.random() < self.success_rate
        if is_success:
            return ValidationResult(valid=True, request_id=request_id, timestamp=datetime.utcnow(), data=data, error=None, metadata={'mock_latency_ms': round(latency_ms, 2), 'request_counter': self._request_counter})
        else:
            error_type = self._random.choices(list(self.failure_patterns.keys()), weights=list(self.failure_patterns.values()))[0]
            error_message = self._generate_error_message(error_type, data)
            return ValidationResult(valid=False, request_id=request_id, timestamp=datetime.utcnow(), data=data, error=error_message, metadata={'mock_latency_ms': round(latency_ms, 2), 'request_counter': self._request_counter, 'error_type': error_type})

    def _generate_error_message(self, error_type: str, data: Dict[str, Any]) -> str:
        """Generate realistic error message based on error type"""
        if error_type == 'validation_error':
            return f'Validation failed for data: {str(data)[:100]}...'
        elif error_type == 'timeout_error':
            return 'Request timed out during validation'
        elif error_type == 'system_error':
            return 'Internal system error during validation'
        else:
            return f'Unknown error type: {error_type}'

    def reset_request_count(self) -> None:
        """Reset internal request counter (for testing)"""
        self._request_counter = 0

    def get_request_count(self) -> int:
        """Get current request count (for testing)"""
        return self._request_counter

class DeterministicMockValidator(MockValidator):
    """
    Deterministic mock validator for reproducible test results.
    Always produces the same sequence of results for given inputs.
    """

    def __init__(self, success_rate: float=0.95, base_latency_ms: float=10.0, latency_variance_ms: float=5.0, seed: int=42):
        super().__init__(success_rate, base_latency_ms, latency_variance_ms)
        self.seed(seed)

    async def validate(self, request_id: int, data: Dict[str, Any]) -> ValidationResult:
        """Deterministic validation based on request_id for predictable success rate"""
        normalized_id = request_id % 1000
        threshold = int(self.success_rate * 1000)
        is_success = normalized_id < threshold
        self._random.seed(request_id)
        latency_ms = self.base_latency_ms + self._random.uniform(-self.latency_variance_ms, self.latency_variance_ms)
        latency_ms = max(0.1, latency_ms)
        await asyncio.sleep(latency_ms / 1000.0)
        if is_success:
            return ValidationResult(valid=True, request_id=request_id, timestamp=datetime.utcnow(), data=data, error=None, metadata={'mock_latency_ms': round(latency_ms, 2), 'request_counter': self._request_counter, 'deterministic_pattern': f'id_{normalized_id}_threshold_{threshold}'})
        else:
            error_type = self._random.choices(list(self.failure_patterns.keys()), weights=list(self.failure_patterns.values()))[0]
            error_message = self._generate_error_message(error_type, data)
            return ValidationResult(valid=False, request_id=request_id, timestamp=datetime.utcnow(), data=data, error=error_message, metadata={'mock_latency_ms': round(latency_ms, 2), 'request_counter': self._request_counter, 'error_type': error_type, 'deterministic_pattern': f'id_{normalized_id}_threshold_{threshold}'})