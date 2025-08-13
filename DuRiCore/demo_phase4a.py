from DuRiCore.trace import emit_trace
"""
Demo script for Phase 4A implementation.
Tests the new clean architecture with ports, adapters, and dependency injection.
"""
import asyncio
import json
from datetime import datetime
from core import create_test_container, create_integration_container, create_stress_test_container, ValidatorPort

async def demo_basic_functionality():
    """Demonstrate basic functionality of the new architecture"""
    emit_trace('info', ' '.join(map(str, ['🚀 Phase 4A Demo: Basic Functionality'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    container = create_test_container()
    emit_trace('info', ' '.join(map(str, [f'📦 Container bindings: {container.get_binding_info()}'])))
    runner = container.create_test_runner()
    scenarios = {'light': {'n_requests': 50, 'max_concurrent': 5}, 'medium': {'n_requests': 100, 'max_concurrent': 10}, 'heavy': {'n_requests': 200, 'max_concurrent': 20}}
    emit_trace('info', ' '.join(map(str, ['\n🏃 Running test scenarios...'])))
    results = await runner.run_scenarios(scenarios)
    emit_trace('info', ' '.join(map(str, ['\n📊 Results Summary:'])))
    emit_trace('info', ' '.join(map(str, ['-' * 30])))
    for (scenario_name, snapshot) in results.items():
        summary = runner.get_scenario_summary(snapshot)
        emit_trace('info', ' '.join(map(str, [f'\n{scenario_name.upper()}:'])))
        for (key, value) in summary.items():
            emit_trace('info', ' '.join(map(str, [f'  {key}: {value}'])))
    return results

async def demo_deterministic_testing():
    """Demonstrate deterministic testing capabilities"""
    emit_trace('info', ' '.join(map(str, ['\n🎯 Phase 4A Demo: Deterministic Testing'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    container = create_test_container()
    validator1 = container.resolve(ValidatorPort, seed=42)
    validator2 = container.resolve(ValidatorPort, seed=42)
    emit_trace('info', ' '.join(map(str, ['🔒 Testing deterministic behavior...'])))
    data = {'test': 'deterministic', 'value': 123}
    result1 = await validator1.validate(1, data)
    result2 = await validator2.validate(1, data)
    emit_trace('info', ' '.join(map(str, [f'Validator 1 result: {result1.valid}, error: {result1.error}'])))
    emit_trace('info', ' '.join(map(str, [f'Validator 2 result: {result2.valid}, error: {result2.error}'])))
    emit_trace('info', ' '.join(map(str, [f'Results identical: {result1.valid == result2.valid and result1.error == result2.error}'])))

async def demo_metrics_isolation():
    """Demonstrate metrics isolation between scenarios"""
    emit_trace('info', ' '.join(map(str, ['\n📈 Phase 4A Demo: Metrics Isolation'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    container = create_test_container()
    runner = container.create_test_runner()
    emit_trace('info', ' '.join(map(str, ['🔄 Running same scenario twice to test isolation...'])))
    result1 = await runner.run_scenario('isolation_test', 50, 5)
    result2 = await runner.run_scenario('isolation_test', 50, 5)
    emit_trace('info', ' '.join(map(str, [f'First run - Total requests: {result1.total_requests}'])))
    emit_trace('info', ' '.join(map(str, [f'Second run - Total requests: {result2.total_requests}'])))
    emit_trace('info', ' '.join(map(str, [f'Metrics properly isolated: {result1.total_requests == result2.total_requests}'])))

async def demo_container_factory():
    """Demonstrate different container configurations"""
    emit_trace('info', ' '.join(map(str, ['\n🏭 Phase 4A Demo: Container Factory'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    unit_container = create_test_container()
    integration_container = create_integration_container()
    stress_container = create_stress_test_container()
    containers = [('Unit Test', unit_container), ('Integration', integration_container), ('Stress Test', stress_container)]
    for (name, container) in containers:
        emit_trace('info', ' '.join(map(str, [f'\n{name} Container:'])))
        bindings = container.get_binding_info()
        for (port, adapter) in bindings.items():
            emit_trace('info', ' '.join(map(str, [f'  {port} → {adapter}'])))

async def demo_error_handling():
    """Demonstrate error handling and retry logic"""
    emit_trace('info', ' '.join(map(str, ['\n⚠️ Phase 4A Demo: Error Handling'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    container = create_test_container()
    validator = container.resolve(ValidatorPort, success_rate=0.3)
    emit_trace('info', ' '.join(map(str, ['🧪 Testing error handling with low success rate validator...'])))
    results = []
    for i in range(10):
        try:
            result = await validator.validate(i + 1, {'test': 'error_handling'})
            results.append(result.valid)
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'Request {i + 1} failed with exception: {e}'])))
            results.append(False)
    success_count = sum(results)
    total_count = len(results)
    success_rate = success_count / total_count if total_count > 0 else 0.0
    emit_trace('info', ' '.join(map(str, [f'Success rate: {success_rate:.2%} ({success_count}/{total_count})'])))

async def main():
    """Main demo function"""
    emit_trace('info', ' '.join(map(str, ['🎉 Phase 4A Clean Architecture Demo'])))
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
    emit_trace('info', ' '.join(map(str, ['Testing the new ports, adapters, and dependency injection system'])))
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
    try:
        await demo_basic_functionality()
        await demo_deterministic_testing()
        await demo_metrics_isolation()
        await demo_container_factory()
        await demo_error_handling()
        emit_trace('info', ' '.join(map(str, ['\n✅ All demos completed successfully!'])))
        emit_trace('info', ' '.join(map(str, ['\n🎯 Phase 4A Key Benefits:'])))
        emit_trace('info', ' '.join(map(str, ['  • Clean separation of concerns'])))
        emit_trace('info', ' '.join(map(str, ['  • Easy testing and mocking'])))
        emit_trace('info', ' '.join(map(str, ['  • Deterministic test results'])))
        emit_trace('info', ' '.join(map(str, ['  • Metrics isolation'])))
        emit_trace('info', ' '.join(map(str, ['  • Flexible dependency injection'])))
        emit_trace('info', ' '.join(map(str, ["  • No more '언발에 오줌누기'! 🚫💦"])))
    except Exception as e:
        emit_trace('info', ' '.join(map(str, [f'\n❌ Demo failed with error: {e}'])))
        import traceback
        traceback.print_exc()
if __name__ == '__main__':
    asyncio.run(main())