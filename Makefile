AS_OF_DAY ?= 36
VAR ?= A
SEED ?= 42
CONFIG ?= configs/day36.yaml
PYTHONPATH := $(PWD)

GATE_RESULTS ?= outputs/day$(AS_OF_DAY)/var_$(VAR)/results.json
POLICY ?= policies/promotion.yaml

.PHONY: run clean check promote test gate day41 day42 day43 validate-logs rollup gate-metrics

check:
	@test -f $(CONFIG) || (echo "Missing $(CONFIG)"; exit 1)

run: check
	@echo "Running day $(AS_OF_DAY) VAR $(VAR) SEED $(SEED)"
	PYTHONPATH=$(PYTHONPATH) python -m src.pipeline.run --day $(AS_OF_DAY) --variant $(VAR) --seed $(SEED) --config $(CONFIG)

clean:
	rm -rf .cache .pytest_cache
	find outputs -mindepth 1 -maxdepth 1 ! -name '.gitkeep' -exec rm -rf {} +

promote:
	python scripts/promotion_gate.py outputs/day$(AS_OF_DAY)/var_$(VAR)/results.json policies/promotion.yaml

test:
	python -m pytest -q

gate:
	@echo "Gating $(GATE_RESULTS) with $(POLICY)"
	python scripts/promotion_gate.py $(GATE_RESULTS) $(POLICY)

# Day41~43: PoU Pilot Log Generation
day41:
	@echo "Generating Day41 medical pilot logs..."
	python tools/pilot_log_append.py --domain medical --sessions 20 --canary 0.1
	@echo "Generating Day41 rehab pilot logs..."
	python tools/pilot_log_append.py --domain rehab --sessions 15 --canary 0.05
	@echo "Generating Day41 coding pilot logs..."
	python tools/pilot_log_append.py --domain coding --sessions 25 --canary 0.05

day42:
	@echo "Generating Day42 medical pilot logs..."
	python tools/pilot_log_append.py --domain medical --sessions 30 --canary 0.15
	@echo "Generating Day42 rehab pilot logs..."
	python tools/pilot_log_append.py --domain rehab --sessions 25 --canary 0.10
	@echo "Generating Day42 coding pilot logs..."
	python tools/pilot_log_append.py --domain coding --sessions 35 --canary 0.10

day43:
	@echo "Generating Day43 medical pilot logs..."
	python tools/pilot_log_append.py --domain medical --sessions 40 --canary 0.20
	@echo "Generating Day43 rehab pilot logs..."
	python tools/pilot_log_append.py --domain rehab --sessions 35 --canary 0.15
	@echo "Generating Day43 coding pilot logs..."
	python tools/pilot_log_append.py --domain coding --sessions 45 --canary 0.15

validate-logs:
	@echo "Validating pilot logs..."
	@for log_file in medical_pilot_v2_logs/logs.jsonl med_pilot_v2_logs/logs.jsonl rehab_pilot_v2_logs/logs.jsonl coding_pilot_v2_logs/logs.jsonl code_pilot_v2_logs/logs.jsonl; do \
		if [ -f "$$log_file" ]; then \
			echo "Validating $$log_file..."; \
			python tools/validate_pilot_logs.py --log-file "$$log_file" || exit 1; \
		fi; \
	done

rollup:
	@echo "Rolling up pilot metrics..."
	python tools/pilot_metrics_rollup.py --output slo_sla_dashboard_v1/metrics.json

gate-metrics: rollup
	@echo "Checking metrics against thresholds..."
	@python -c "import json, sys; m=json.load(open('slo_sla_dashboard_v1/metrics.json')); th={'p_error_max': 0.02, 'p_timeout_max': 0.02, 'explain_min': 0.70}; bad=[]; [bad.append(f'p_error {m[\"p_error\"]:.3f} > {th[\"p_error_max\"]}') if m['p_error'] > th['p_error_max'] else None]; [bad.append(f'p_timeout {m[\"p_timeout\"]:.3f} > {th[\"p_timeout_max\"]}') if m['p_timeout'] > th['p_timeout_max'] else None]; [bad.append(f'explain {m[\"explain_score\"]:.3f} < {th[\"explain_min\"]}') if m['explain_score'] < th['explain_min'] else None]; print('❌ GATE=FAIL | ' + '; '.join(bad)) if bad else print('✅ GATE=PASS'); sys.exit(2 if bad else 0)"