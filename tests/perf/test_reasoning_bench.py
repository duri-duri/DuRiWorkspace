import random

import pytest

from logical_reasoning_engine import ReasoningEngine


@pytest.fixture(scope="module")
def eng():
    return ReasoningEngine()


# P50/P95를 가를 수 있게 짧은 작업을 여러 번 반복
@pytest.mark.benchmark(group="reasoning.process")
def test_reasoning_math_bench(benchmark, eng):
    payload = {"query": "1+1", "context": "math"}
    benchmark(lambda: eng.process(payload))


@pytest.mark.benchmark(group="reasoning.process")
def test_reasoning_general_bench(benchmark, eng):
    xs = ["weather", "status", "heartbeat", "diagnose", "ping"]

    def run():
        payload = {"query": random.choice(xs), "context": "general"}
        return eng.process(payload)

    benchmark(run)


@pytest.mark.benchmark(group="reasoning.process")
def test_reasoning_advanced_bench(benchmark, eng):
    payload = {"query": "analyze clinical pattern", "context": "advanced"}
    benchmark(lambda: eng.process(payload))
