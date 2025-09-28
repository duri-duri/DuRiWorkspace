.PHONY: phase25.L0L1 phase25.L2L4 phase25.all

phase25.L0L1:
	pytest -q tests/phases/test_phase25_smoke.py tests/phases/test_phase25_contract.py

phase25.L2L4:
	pytest -q tests/phases/test_phase25_behavior.py tests/phases/test_phase25_guard.py tests/phases/test_phase25_invariance.py

phase25.all: phase25.L0L1 phase25.L2L4