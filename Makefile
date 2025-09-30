.PHONY: phase25.L0L1 phase25.L2L4 phase25.all ab.test ab.replay ab.power ab.legacy

phase25.L0L1:
	pytest -q tests/phases/test_phase25_smoke.py tests/phases/test_phase25_contract.py

phase25.L2L4:
	pytest -q tests/phases/test_phase25_behavior.py tests/phases/test_phase25_guard.py tests/phases/test_phase25_invariance.py

phase25.all: phase25.L0L1 phase25.L2L4

# A/B 테스트 통합 타겟
ab.test:
	pytest -q tests/test_ab_runner_smoke.py tests/test_ab_runner.py tests/test_ab_srm_aa.py tests/test_pou_d7.py

ab.replay:
	python3 ab_test_runner.py --config configs/experiments/example.yaml --input data/demo_ab.csv --metric latency_ms --group variant --output logs/ab

ab.power:
	python3 tools/ab_power_calc.py --alpha 0.05 --power 0.8 --effect-size 0.2

ab.legacy:
	$(MAKE) -C DuRi_Day11_15_starter run AS_OF_DAY=36 VAR=A SEED=42
	$(MAKE) -C DuRi_Day11_15_starter run AS_OF_DAY=36 VAR=B SEED=42

ab.replay.rehab:
	python3 ab_test_runner.py --config configs/experiments/rehab_safety.yaml \
	 --input data/rehab_day32.csv --metric safety_ok --group variant \
	 --output logs/ab --gate-policy policies/promotion.yaml --exp-id rehab_safety_d32

ab.report.tree:
	find logs/ab -type f -name "*.jsonl" | sed 's|.*/logs/ab/||' | sort

# Day 37 PoU 7일차 유지율 분석
pou.d7.extract:
	python3 tools/pou_day7_extract.py --synthetic --out data/pou_day7.csv --n-users 1000

pou.d7.test:
	python3 ab_test_runner.py --config configs/experiments/pou_d7.yaml --input data/pou_day7.csv --metric retained_d7 --group variant --output logs/ab --gate-policy policies/promotion.yaml --exp-id pou_d7

pou.d7.all: pou.d7.extract pou.d7.test