from DuRiCore.trace import emit_trace
"""
Core package for clean architecture implementation.
Provides ports, test runner, and dependency injection container.
"""
from .ports import ValidationResult, MetricsSnapshot, ValidatorPort, MetricsPort, ClockPort, RandomPort, TestRunnerPort
from .errors import ValidationError, TransientError, SystemError, ErrorPolicy
from .config import Phase4BConfig, load_thresholds
from .metrics import StressTestMetrics, Summary
from .test_runner import HybridTestRunner
from .container import TestContainer, ProductionContainer, TestEnvironmentFactory, create_test_container, create_integration_container, create_stress_test_container
__all__ = ['ValidationResult', 'MetricsSnapshot', 'ValidatorPort', 'MetricsPort', 'ClockPort', 'RandomPort', 'TestRunnerPort', 'HybridTestRunner', 'TestContainer', 'ProductionContainer', 'TestEnvironmentFactory', 'create_test_container', 'create_integration_container', 'create_stress_test_container', 'ValidationError', 'TransientError', 'SystemError', 'ErrorPolicy', 'Phase4BConfig', 'load_thresholds', 'StressTestMetrics', 'Summary']