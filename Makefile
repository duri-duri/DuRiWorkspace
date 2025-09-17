AS_OF_DAY ?= 36
VAR ?= A
SEED ?= 42
CONFIG ?= configs/day36.yaml
PYTHONPATH := $(PWD)
PY ?= python3

GATE_RESULTS ?= outputs/day$(AS_OF_DAY)/var_$(VAR)/results.json
POLICY ?= policies/promotion.yaml

.PHONY: run clean check promote test gate day41 day42 day43 day44 day45 day46 day47 day48 day49 day50 validate-logs rollup gate-metrics report

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

# Python runtime
PY ?= python3

rollup:
	@echo "Rolling up pilot metrics..."
	$(PY) tools/pilot_metrics_rollup.py --output slo_sla_dashboard_v1/metrics.json

gate-metrics: rollup
	@echo "Checking metrics against thresholds..."
	@python -c "import json, sys; m=json.load(open('slo_sla_dashboard_v1/metrics.json')); th={'p_error_max': 0.02, 'p_timeout_max': 0.02, 'explain_min': 0.70}; bad=[]; [bad.append(f'p_error {m[\"p_error\"]:.3f} > {th[\"p_error_max\"]}') if m['p_error'] > th['p_error_max'] else None]; [bad.append(f'p_timeout {m[\"p_timeout\"]:.3f} > {th[\"p_timeout_max\"]}') if m['p_timeout'] > th['p_timeout_max'] else None]; [bad.append(f'explain {m[\"explain_score\"]:.3f} < {th[\"explain_min\"]}') if m['explain_score'] < th['explain_min'] else None]; print('❌ GATE=FAIL | ' + '; '.join(bad)) if bad else print('✅ GATE=PASS'); sys.exit(2 if bad else 0)"

report:
	@mkdir -p reports
	@$(PY) tools/pou_weekly_report.py --out reports/pou_midterm_report.md

day44: rollup report
	@echo "Day44 done -> reports/pou_midterm_report.md"

day45:
	@$(PY) tools/auto_patch_weekly_stats.py --threshold 0.80
	@echo "Day45 done -> auto_patch_weekly_stats.json"

day46:
	@echo "Generating model card v1..."
	@$(PY) tools/gen_model_card.py && echo "Day46 done -> model_card_v1.md"

day47:
	@echo "Seeding patent drafts..."
	@ls -la patent_drafts && echo "Day47 done -> patent_drafts/"

day48:
	@echo "Probing cost & writing plan..."
	@$(PY) tools/cost_probe.py > reports/cost_probe.json || true
	@echo "Day48 done -> cost_optimization_plan.md, reports/cost_probe.json"

day49:
	@echo "Calculating retention rates..."
	@$(PY) tools/retention_calc.py --out pou_retention_day21.json
	@echo "Day49 done -> pou_retention_day21.json"

day50:
	@echo "Auto-tuning objective function v2..."
	@$(PY) tools/objective_tuning_v2.py
	@echo "Day50 done -> configs/objective_params_v2.yaml, reports/objective_tuning_summary.json"

.PHONY: gate-objective
gate-objective:
	@$(PY) -c "import json,sys; s=json.load(open('reports/objective_tuning_summary.json')); ok = s.get('tuning_success', False); print('J_proxy =', s.get('j_proxy')); sys.exit(0 if ok else 1)"

.PHONY: use-start use-check use-report use-stop

use-start:
	@python3 -c "import yaml,sys; p='configs/canary_settings.yaml'; cfg=yaml.safe_load(open(p)) if open(p).read().strip() else {}; cfg={'medical':{'canary':0.05},'rehab':{'canary':0.0},'coding':{'canary':0.0}}; open(p,'w').write(yaml.dump(cfg,allow_unicode=True,default_flow_style=False)); print('Set canary -> medical 5%, others 0%')"
	@git fetch origin
	@branch=ops/canary-5-medical-$(shell date +%F-%H%M%S); \
	git switch -c $$branch; \
	git add configs/canary_settings.yaml; \
	git commit -m "ops: canary 5% (medical), others 0%" || true; \
	git push -u origin $$branch; \
	(gh pr create --base main --head $$branch \
	  --title "ops: canary 5% (medical)" \
	  --body "Enable medical canary at 5%. Others 0%. Includes use-mode wiring." \
	 || echo "➡️  GitHub UI에서 $$branch 로 PR 열어주세요"); \
	git switch main; git reset --hard origin/main

use-check:
	@echo "Rolling metrics & tuning objective..."
	make rollup
	make day49
	make day50
	make gate-objective

use-report:
	@echo "Objective summary:"
	@cat reports/objective_tuning_summary.json 2>/dev/null | jq '.j_proxy, .input_metrics, .scores' || true

use-stop:
	@python3 -c "import yaml, os; p='configs/canary_settings.yaml'; d = yaml.safe_load(open(p)) if os.path.exists(p) else {}; [d.setdefault(k, {}) for k in ('medical','rehab','coding')]; [d[k].update({'canary': 0.00}) for k in d]; open(p,'w',encoding='utf-8').write(yaml.dump(d, allow_unicode=True, default_flow_style=False)); print('Set canary -> all 0% (panic)')"
	git add configs/canary_settings.yaml
	git commit -m "ops: canary 0% (panic)" || true
	git push || true

.PHONY: gate-exit
gate-exit:
	@python3 -c "import json,os,sys,time; jload=lambda p: json.load(open(p,encoding='utf-8')) if os.path.exists(p) and os.path.getsize(p)>0 else {}; m=jload('slo_sla_dashboard_v1/metrics.json'); r=jload('pou_retention_day21.json'); n=m.get('n'); p_err=m.get('p_error'); p_to=m.get('p_timeout'); expl=m.get('explain'); d21=r.get('retention_d21') or (((r.get('retention',{}) or {}).get('all',{}) or {}).get('rates',{}) or {}).get('d21'); fmt=lambda x: '—' if x is None else (f'{x:.3f}' if isinstance(x,(int,float)) else str(x)); print(f'n={n or 0}  p_error={fmt(p_err)}  p_timeout={fmt(p_to)}  explain={fmt(expl)}  d21={fmt(d21)}'); THR_PERR=0.02; THR_PTIME=0.02; THR_EXPL=0.70; THR_D21=0.00; MIN_N=30; ok=True; reasons=[]; (lambda: [reasons.append(f'insufficient n ({n or 0}<{MIN_N})') for _ in [None] if not n or n < MIN_N])(), (lambda: [reasons.append(f'p_error {fmt(p_err)}>{THR_PERR}') for _ in [None] if (p_err is None) or (p_err > THR_PERR)])(), (lambda: [reasons.append(f'p_timeout {fmt(p_to)}>{THR_PTIME}') for _ in [None] if (p_to is None) or (p_to > THR_PTIME)])(), (lambda: [reasons.append(f'explain {fmt(expl)}<{THR_EXPL}') for _ in [None] if (expl is None) or (expl < THR_EXPL)])(), (lambda: [reasons.append('retention_d21 missing' if d21 is None else f'd21 {fmt(d21)}<{THR_D21}') for _ in [None] if (d21 is None) or (d21 < THR_D21)])(); print('Gate PASSED' if not reasons else 'Gate FAILED: ' + '; '.join(reasons)); sys.exit(0 if not reasons else 2)"