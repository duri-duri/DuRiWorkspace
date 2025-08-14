from DuRiCore.trace import emit_trace
"""
Dependency injection container for clean architecture.
Manages port-adapter bindings and provides factory methods.
"""
from typing import Dict, Type, Any, Optional
from .ports import ValidatorPort, MetricsPort, ClockPort, RandomPort, TestRunnerPort
from .test_runner import HybridTestRunner

class TestContainer:
    """
    Dependency injection container for test scenarios.
    Manages port-adapter bindings and provides factory methods.
    """

    def __init__(self):
        self._bindings: Dict[Type, Type] = {}
        self._instances: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._setup_default_bindings()

    def _setup_default_bindings(self) -> None:
        """Setup default port-adapter bindings"""
        from adapters.metrics.in_memory_metrics import InMemoryMetrics
        from adapters.mock.mock_validator import MockValidator, DeterministicMockValidator
        from adapters.clock.system_clock import SystemClock, MockClock
        from adapters.random.system_random import SystemRandom, ControlledRandom
        self.bind(ValidatorPort, MockValidator)
        self.bind(MetricsPort, InMemoryMetrics)
        self.bind(ClockPort, MockClock)
        self.bind(RandomPort, ControlledRandom)

    def bind(self, port_type: Type, adapter_type: Type) -> None:
        """Bind a port interface to an adapter implementation"""
        self._bindings[port_type] = adapter_type
        if port_type in self._instances:
            del self._instances[port_type]

    def bind_singleton(self, port_type: Type, instance: Any) -> None:
        """Bind a port interface to a singleton instance"""
        self._singletons[port_type] = instance

    def resolve(self, port_type: Type, **kwargs) -> Any:
        """Resolve a port interface to an implementation instance"""
        if port_type in self._singletons:
            return self._singletons[port_type]
        if port_type in self._instances:
            return self._instances[port_type]
        if port_type in self._bindings:
            adapter_type = self._bindings[port_type]
            instance = adapter_type(**kwargs)
            self._instances[port_type] = instance
            return instance
        raise ValueError(f'No binding found for {port_type}')

    def create_test_runner(self, **kwargs) -> TestRunnerPort:
        """Create a test runner with resolved dependencies"""
        validator = self.resolve(ValidatorPort)
        metrics = self.resolve(MetricsPort)
        clock = self.resolve(ClockPort)
        return HybridTestRunner(validator=validator, metrics=metrics, clock=clock, **kwargs)

    def reset(self) -> None:
        """Reset all instances (useful for test isolation)"""
        self._instances.clear()

    def get_binding_info(self) -> Dict[str, str]:
        """Get information about current bindings"""
        return {port_type.__name__: adapter_type.__name__ for (port_type, adapter_type) in self._bindings.items()}

class ProductionContainer(TestContainer):
    """
    Production container with real system implementations.
    Suitable for production and integration testing.
    """

    def _setup_default_bindings(self) -> None:
        """Setup production bindings"""
        from adapters.metrics.in_memory_metrics import InMemoryMetrics
        from adapters.mock.mock_validator import MockValidator, DeterministicMockValidator
        from adapters.clock.system_clock import SystemClock, MockClock
        from adapters.random.system_random import SystemRandom, ControlledRandom
        self.bind(ValidatorPort, MockValidator)
        self.bind(MetricsPort, InMemoryMetrics)
        self.bind(ClockPort, SystemClock)
        self.bind(RandomPort, SystemRandom)

class TestEnvironmentFactory:
    """
    Factory for creating different test environments.
    Provides predefined configurations for common testing scenarios.
    """

    @staticmethod
    def create_unit_test_container() -> TestContainer:
        """Create container optimized for unit testing"""
        container = TestContainer()
        container.bind(ValidatorPort, DeterministicMockValidator)
        container.bind(ClockPort, MockClock)
        container.bind(RandomPort, ControlledRandom)
        return container

    @staticmethod
    def create_integration_test_container() -> TestContainer:
        """Create container for integration testing"""
        container = TestContainer()
        container.bind(ValidatorPort, MockValidator)
        container.bind(ClockPort, SystemClock)
        container.bind(RandomPort, SystemRandom)
        return container

    @staticmethod
    def create_stress_test_container() -> TestContainer:
        """Create container optimized for stress testing"""
        container = TestContainer()
        container.bind(ValidatorPort, MockValidator)
        container.bind(MetricsPort, InMemoryMetrics)
        container.bind(ClockPort, SystemClock)
        container.bind(RandomPort, SystemRandom)
        return container

    @staticmethod
    def create_custom_container(validator_type: Type[ValidatorPort]=None, metrics_type: Type[MetricsPort]=None, clock_type: Type[ClockPort]=None, random_type: Type[RandomPort]=None) -> TestContainer:
        """Create container with custom bindings"""
        container = TestContainer()
        if validator_type:
            container.bind(ValidatorPort, validator_type)
        if metrics_type:
            container.bind(MetricsPort, metrics_type)
        if clock_type:
            container.bind(ClockPort, clock_type)
        if random_type:
            container.bind(RandomPort, random_type)
        return container

def create_test_container() -> TestContainer:
    """Create a default test container"""
    return TestEnvironmentFactory.create_unit_test_container()

def create_integration_container() -> TestContainer:
    """Create an integration test container"""
    return TestEnvironmentFactory.create_integration_test_container()

def create_stress_test_container() -> TestContainer:
    """Create a stress test container"""
    return TestEnvironmentFactory.create_stress_test_container()