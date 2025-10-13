.PHONY: phase25.L0L1 phase25.L2L4 phase25.all ab.test ab.replay ab.power ab.legacy

.PHONY: day38.suggest
 day38.suggest:
	@echo "Collecting last CI log..." ; true
	@cat last_ci.log 2>/dev/null | python3 tools/auto_fix_suggester.py || true


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

.PHONY: day38.patch
day38.patch:
	@echo "Generating patches..."
	@python3 tools/patch_generator.py add_import tests/test_example.py duri_common.settings || true
	@echo "Dry-run patching..."
	@echo '{"action":"add_import","file":"tests/test_example.py","module":"duri_common.settings"}' | python3 tools/dry_run_patcher.py || true

# 개발 편의 타깃 3종
.PHONY: clean-deep ci-local pr-autofix
clean-deep:
	@docker compose down --volumes || true
	@docker system prune -f || true
	@echo "Cleaned."

ci-local:
	@pytest -q tests || true
	@python tools/policy_gate.py || true

pr-autofix:
	@gh pr edit $$PR --add-label "auto-fix:suggest" || echo "Set PR environment variable first"

prom-rules-ci:
	@echo "promtool check rules (placeholder)"; promtool --version >/dev/null

grafana-lint:
	@echo "grafana lint (placeholder)"

runbook-quality-guard:
	@echo "runbook guard (placeholder)"

ci-all: prom-rules-ci grafana-lint runbook-quality-guard
	@echo "ci-all done"
