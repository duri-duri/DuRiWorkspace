from duri_finale.phase_25_final_evolution_ai import FinalEvolutionAI

LIMITS = {"error_rate_max": 0.02, "p95_ms_max": 300.0}

def test_guard_error_rate_and_latency():
    fe = FinalEvolutionAI()
    stats = fe.self_check(n=200)
    assert stats["error_rate"] <= LIMITS["error_rate_max"]
    assert stats["p95_ms"] <= LIMITS["p95_ms_max"]
