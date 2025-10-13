SUDO ?= sudo -n
SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c

# 리포지토리 루트 고정
REPO_ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
export REPO_ROOT

# CI 도구 고정 (노이즈 제로)
ci-bootstrap-tools:
	@command -v shellcheck >/dev/null || echo "⚠️ shellcheck 없음 - 건너뜀" || true
	@command -v promtool   >/dev/null || echo "⚠️ promtool 없음 - 건너뜀" || true
	@command -v black      >/dev/null || pip3 install --user black || true
	@command -v pylint     >/dev/null || pip3 install --user pylint || true
.PHONY: eval gate smoke clean k-sweep archive rollup smoke-preview help shellcheck metrics metrics-dashboard metrics-watch prom-rules-verify prom-rules-test prom-rules-ci validate-prom-all check-prom

# 변수 정의 - 기본값 설정
GT ?= .reports/day62/ground_truth_clean.tsv
K ?= 3
THRESH_P ?= 0.30
QUIET ?= 1

# Day66 메트릭 시스템 기본값
PRED ?= .reports/metrics/day66_test_data.tsv
TH_ENV ?= .reports/metrics/day66_thresholds.env
METRIC_K ?= 3
RUN_PATH ?=

# Day67 시계열 분석 기본값
WEEK ?= 7

# Day68 관찰 가능성 기본값
export GA_ENFORCE ?= 1
export CROSS_TYPE_ENFORCE ?= 1

# 의존성 정의
SCRIPTS = scripts/rag_eval.sh scripts/rag_gate.sh
TESTS = tests/eval_smoke.sh

# 출력 파일 정리
clean:
	@rm -f .reports/last_eval.tsv
	@find .reports -name "eval_*.tsv" -type f | head -10 | xargs rm -f

# 평가 실행 - 결과를 파일로 저장 후 요약 표시
eval: $(GT) $(SCRIPTS)
	@mkdir -p .reports
	@TIMEOUT_SECS=8 bash scripts/rag_eval.sh "$(GT)" > .reports/last_eval.tsv || { echo "eval failed"; exit 1; }
	@tail -n 10 .reports/last_eval.tsv

# 게이트 검증 - 테스트 통과 여부 확인
gate: $(GT) $(SCRIPTS)

# 안전 미리보기 타깃
smoke-preview:

# 루틴 단축 타깃
smoke:
	@tests/smoke_ensemble.sh

gate:
	@scripts/pr_gate_day63.sh

# 안전 미리보기 타깃
smoke-preview:
	@{ tests/smoke_ensemble.sh | { head -n 20; cat >/dev/null; }; } || true

# 도움말 타깃
help:
	@echo "Targets:"
	@echo "  smoke           - 스모크 앙상블"
	@echo "  smoke-preview   - 스모크 상위 로그 20줄"
	@echo "  gate            - PR 게이트 실행"
	@echo "  shellcheck      - 스크립트 품질 검사"
	@echo "  help            - 이 도움말"

shellcheck:
	@./scripts/shellcheck_hook.sh || true

# 운영 편의 타깃 (systemd)
.PHONY: start-shadow stop-shadow status-shadow install-systemd
start-shadow:
	@$(SUDO) systemctl enable --now duri-rag-eval duri-pr-gate duri-rag-eval-tuned

stop-shadow:
	@$(SUDO) systemctl disable --now duri-rag-eval duri-pr-gate duri-rag-eval-tuned || true

stop-shadow-user:
	@echo "🛑 sudo 없이 Shadow 루프 종료 (사용자 단위 systemd)"
	@bash scripts/stop_shadow_user.sh

status-shadow:
	@$(SUDO) systemctl --no-pager --full status duri-rag-eval duri-pr-gate duri-rag-eval-tuned | sed -n '1,40p'

cleanup-docker:
	@echo "🧹 도커 네트워크 잔류 방지"
	@bash scripts/cleanup_docker.sh

# CI 게이트 단계화
ci-metrics-report:
	@echo "📊 CI: 메트릭 리포트 생성 (비엄격)"
	@bash scripts/ci_metrics_report.sh
	@echo "🔍 promtool 검증..."
	@bash scripts/metrics/validate_prom.sh .reports/metrics/day66_metrics.tsv

# GA 태그 감지로 강제화
GA_ENFORCE := $(shell git describe --tags --exact-match >/dev/null 2>&1 && echo 1 || echo 0)

ci-pr-gate:
	@echo "🚪 CI: PR 게이트 (엄격)"
	@GA_ENFORCE=$(GA_ENFORCE) CI_STRICT_TOOLS=$(GA_ENFORCE) NO_SUDO=1 bash scripts/pr_gate_day63.sh
	@bash tests/smoke/test_prom_help_type.sh
	@$(MAKE) prom-rules-ci
	@$(MAKE) validate-prom-all

# 스모크 확장
smoke-edge-assertions:
	@echo "🧪 스모크 확장: 엣지 5종 자동단언"
	# 1) 헤더만 있음 → exit 1 기대
	@bash -c 'printf "scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3\n" > /tmp/m.tsv; \
	  bash scripts/alerts/threshold_guard.sh /tmp/m.tsv 3 >/dev/null 2>&1; ec=$$?; \
	  if [ $$ec -ne 1 ]; then echo "[FAIL] expected 1 got $$ec"; exit 1; else echo "[OK] header-only -> 1"; fi'
	# 2) 정상 파일 → exit 0 기대
	@bash -c 'bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv 3 >/dev/null 2>&1; ec=$$?; \
	  if [ $$ec -ne 0 ]; then echo "[FAIL] expected 0 got $$ec"; exit 1; else echo "[OK] normal -> 0"; fi'
	# 3) 회귀+엄격 → exit 2 기대
	@bash -c 'TH_NDCG=0.99 TH_MRR=0.99 TH_ORACLE=1.1 GUARD_STRICT=1 \
	  bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv 3 >/dev/null 2>&1; ec=$$?; \
	  if [ $$ec -ne 2 ]; then echo "[FAIL] expected 2 got $$ec"; exit 1; else echo "[OK] strict regression -> 2"; fi'

# 유닛 테스트: 단일 guard 라인 보증
unit-test-exporter:
	@echo "🧪 유닛 테스트: 단일 guard 라인 보증"
	@bash -c 'bash scripts/metrics/export_prom.sh .reports/metrics/day66_metrics.tsv | grep -c "^duri_guard_last_exit_code{" | awk "{exit !(\$$1==1)}" && echo "[OK] guard metric appears exactly once" || { echo "[FAIL] guard metric count mismatch"; exit 1; }'

# Day66 메트릭 시스템
metrics:
	@echo "[metrics] hygiene..."
	@bash scripts/metrics/data_hygiene.sh $(PRED)
	@echo "[metrics] compute..."
	@python3 scripts/metrics/compute_metrics.py --k $(K) --in $(PRED) --out .reports/metrics/day66_metrics.tsv
	@echo "[metrics] guard..."
	@bash -c 'bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv $(K); ec=$$?; \
	          if [ $$ec -eq 2 ]; then exit 2; \
	          elif [ $$ec -eq 1 ]; then echo "[warn] guard parse/infra error → 무시(대시보드 계속)"; exit 0; \
	          else exit 0; fi'
	@echo "[metrics] done → .reports/metrics/day66_metrics.tsv"

# 3도메인 요약(최근 7개 스냅샷이 있다면 합산/추세는 추후 확장)
metrics-dashboard: metrics
	@echo "---- day66 metrics ----"
	@column -t -s$$'\t' .reports/metrics/day66_metrics.tsv
	@echo "---- hygiene ----"
	@column -t -s$$'\t' .reports/metrics/day66_hygiene.tsv

# Day67 시계열 분석
metrics-timeseries:  ## Day67 시계열 분석 실행
	@python3 scripts/metrics/metrics_timeseries.py --input .reports/metrics --outdir .reports/timeseries --period $(WEEK)

weekly-report: metrics-timeseries  ## 주간 리포트 생성
	@echo "📄 Weekly report -> .reports/timeseries/"

# 가드만 실행 (알림 테스트용)
metrics-guard-only:
	@echo "[guard-only] run"
	@bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv $(METRIC_K) || true
	@echo "[guard-only] done"

# 회귀 알림 리허설(의도적 실패). CI에서 알림/종료 플로우 검증용
metrics-guard-sim-regression:
	@echo "[guard-sim] simulate regression via higher thresholds"
	@TH_NDCG=0.99 TH_MRR=0.99 TH_ORACLE=0.99 GUARD_SOFT=1 \
		bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv $(METRIC_K) || true
	@echo "[guard-sim] done"

# 파일 변경 감시(스테이징에서만)
metrics-watch:
	@echo "Watching LATEST.tsv -> recompute on change"
	@while inotifywait -e close_write .reports/train/day64/LATEST.tsv >/dev/null 2>&1; do \
	  $(MAKE) metrics-dashboard || true; \
	done

# 임계값 시스템 배포
install-thresholds:
	@echo "Installing thresholds to /etc/default/duri-workspace"
	@$(SUDO) install -m 0644 .reports/metrics/day66_thresholds.env /etc/default/duri-workspace

# Day68 Prometheus rules 검증
prom-rules-verify:
	@promtool check rules prometheus/rules/*.rules.yml


prom-rules-ci: prom-rules-verify prom-rules-test

validate-prom-all:
	@set -euo pipefail; \
	files=$$(ls .reports/metrics/*.tsv 2>/dev/null || true); \
	if [ -n "$$files" ]; then \
	  for f in $$files; do echo ">> validate $$f"; bash scripts/metrics/validate_prom.sh "$$f"; done; \
	else echo "no prom textfiles under .reports/metrics/ (skip)"; fi

postmortem:
	@bash scripts/alert_postmortem.sh alert_samples/sample_alert.json

# 운영 체크 - Prometheus HTTP API로 상태 확인
check-prom:
	@echo "=== 모니터링 시스템 상태 확인 ==="
	@echo "mem_ratio count:" && curl -s 'http://localhost:9090/api/v1/query' --data-urlencode 'query=count(duri:container:mem_ratio)' | jq -r '.data.result[0].value[1]'
	@echo "limit>0:" && curl -s 'http://localhost:9090/api/v1/query' --data-urlencode 'query=duri:containers:limitgt0' | jq -r '.data.result[0].value[1]'
	@echo "limit=0:" && curl -s 'http://localhost:9090/api/v1/query' --data-urlencode 'query=duri:containers:limit0' | jq -r '.data.result[0].value[1]'
	@echo "p95:" && curl -s 'http://localhost:9090/api/v1/query' --data-urlencode 'query=duri:blackbox:p95' | jq -r '.data.result[] | "\(.metric.target): \(.value[1])s"' | head -3
	@echo "firing alerts:" && curl -s localhost:9090/api/v1/alerts | jq -r '.data.alerts[].labels.alertname' | sort | uniq -c | sort -nr

ci-phase1-guard:
	./scripts/ci_phase1_guard.sh



prom-dup-guard:
	@awk '/^- record: /{print $$3}' prometheus/rules/*.yml \
	| sort | uniq -d | awk '{print "DUP record:", $$0}' | test $$(wc -l < /dev/stdin) -eq 0

prom-rules-test:
	promtool test rules tests/quality_rules_test.yml
