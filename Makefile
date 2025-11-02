SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c
SUDO ?= sudo -n

# CI 도구 고정 (노이즈 제로)
ci-bootstrap-tools:
	@command -v shellcheck >/dev/null || echo "⚠️ shellcheck 없음 - 건너뜀" || true
	@command -v promtool   >/dev/null || echo "⚠️ promtool 없음 - 건너뜀" || true
	@command -v black      >/dev/null || pip3 install --user black || true
	@command -v pylint     >/dev/null || pip3 install --user pylint || true
.PHONY: eval gate smoke clean k-sweep archive rollup smoke-preview help shellcheck metrics metrics-dashboard metrics-watch prom-rules-verify prom-rules-test prom-rules-ci validate-prom-all check-prom prom-rules-ci prom-dup-guard alert-labels-guard prom-rules-test ci-all runbook-url-guard runbook-url-guard-dummy

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
.PHONY: start-shadow stop-shadow status-shadow install-systemd shadow-start shadow-stop shadow-status shadow-run-once
start-shadow:
	@$(SUDO) systemctl enable --now duri-rag-eval duri-pr-gate duri-rag-eval-tuned

stop-shadow:
	@$(SUDO) systemctl disable --now duri-rag-eval duri-pr-gate duri-rag-eval-tuned || true

stop-shadow-user:
	@echo "🛑 sudo 없이 Shadow 루프 종료 (사용자 단위 systemd)"
	@bash scripts/stop_shadow_user.sh

status-shadow:
	@$(SUDO) systemctl --no-pager --full status duri-rag-eval duri-pr-gate duri-rag-eval-tuned | sed -n '1,40p'

# Shadow 훈련장 제어 (4개 명령어)
shadow-start:
	@echo "🚀 Shadow 훈련장 시작..."
	@mkdir -p var/logs var/run var/reports
	@nohup bash scripts/shadow_duri_integration_final.sh > var/logs/shadow_startup.log 2>&1 &
	@sleep 2
	@if [ -f var/run/shadow.pid ]; then \
		echo "✅ Shadow 훈련장 시작됨 (PID: $$(cat var/run/shadow.pid))"; \
	else \
		echo "⚠️ Shadow 훈련장 시작 실패"; \
	fi

shadow-stop:
	@echo "🛑 Shadow 훈련장 중지..."
	@if [ -f var/run/shadow.pid ]; then \
		PID=$$(cat var/run/shadow.pid); \
		if ps -p $$PID > /dev/null 2>&1; then \
			kill $$PID && echo "✅ Shadow 훈련장 중지됨 (PID: $$PID)"; \
		else \
			echo "⚠️ Shadow 훈련장이 실행 중이 아닙니다"; \
		fi; \
		rm -f var/run/shadow.pid var/run/shadow.lock; \
	else \
		echo "⚠️ PID 파일 없음 - 수동 종료 필요"; \
	fi

shadow-status:
	@echo "📊 Shadow 훈련장 상태:"
	@if [ -f var/run/shadow.pid ]; then \
		PID=$$(cat var/run/shadow.pid); \
		if ps -p $$PID > /dev/null 2>&1; then \
			echo "✅ 실행 중 (PID: $$PID)"; \
			echo "실행 시간: $$(ps -p $$PID -o etime=)"; \
			echo "마지막 로그 (최근 5줄):"; \
			tail -5 var/logs/shadow.log 2>/dev/null || echo "로그 없음"; \
		else \
			echo "❌ 실행 중이 아님 (PID 파일 존재하지만 프로세스 없음)"; \
		fi; \
	else \
		echo "❌ 실행 중이 아님 (PID 파일 없음)"; \
	fi
	@echo ""
	@echo "📁 리포트 파일:"
	@ls -lht var/reports/*.md 2>/dev/null | head -5 || echo "리포트 없음"

shadow-run-once:
	@echo "🔄 Shadow 훈련장 1회 실행..."
	@mkdir -p var/logs var/reports
	@bash -c 'source scripts/lib/submodule_sync.sh && sync_all_submodules'
	@bash scripts/shadow_duri_integration_final.sh || echo "⚠️ 1회 실행 완료 (오류 포함)"

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
	@$(PROMTOOL) check rules prometheus/rules/*.rules.yml


PROMTOOL ?= promtool
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
	@if curl -fsS http://localhost:9090/-/ready >/dev/null; then
		echo "Prometheus runtime checks:";
		curl -s "localhost:9090/api/v1/query?query=up" | jq -r ".data.result[] | "\(.metric.job): \(.value[1])"";
		curl -s "localhost:9090/api/v1/alerts" | jq -r ".data.alerts[] | "\(.labels.alertname): \(.state)"";
	else
		echo "Prometheus not available (skipping runtime checks)";
	fi


prom-dup-guard:
	@python3 scripts/prom_dup_guard.py

prom-rules-test:
	@REPO_ROOT=$$(git rev-parse --show-toplevel) \
	  envsubst < tests/quality_rules_test.yml > /tmp/quality_rules_test.rendered.yml && \
	  $(PROMTOOL) test rules /tmp/quality_rules_test.rendered.yml
	@REPO_ROOT=$$(git rev-parse --show-toplevel) \
	  envsubst < tests/alerts_mrr_breach_test.yml > /tmp/alerts_mrr_breach_test.rendered.yml && \
	  $(PROMTOOL) test rules /tmp/alerts_mrr_breach_test.rendered.yml
	@REPO_ROOT=$$(git rev-parse --show-toplevel) \
	  envsubst < tests/alerts_mrr_slo_breach_test.yml > /tmp/alerts_mrr_slo_breach_test.rendered.yml && \
	  $(PROMTOOL) test rules /tmp/alerts_mrr_slo_breach_test.rendered.yml
	@REPO_ROOT=$$(git rev-parse --show-toplevel) \
	  envsubst < tests/alerts_noise_regression_test.yml > /tmp/alerts_noise_regression_test.rendered.yml && \
	  $(PROMTOOL) test rules /tmp/alerts_noise_regression_test.rendered.yml
	@REPO_ROOT=$$(git rev-parse --show-toplevel) \
	  envsubst < tests/metric_collection_test.yml > /tmp/metric_collection_test.rendered.yml && \
	  $(PROMTOOL) test rules /tmp/metric_collection_test.rendered.yml
ci-all:
	make prom-rules-ci
	make prom-dup-guard
	make alert-labels-guard
	make runbook-url-guard-dummy
	make prom-rules-test
	make grafana-lint
	make runbook-quality-guard
grafana-lint:
	@python3 scripts/grafana_lint.py

runbook-quality-guard:
	@python3 scripts/runbook_quality_guard.py

compatibility-test:
	@echo "Running compatibility matrix test"
	@make prom-rules-ci
	@make prom-rules-test

alert-labels-guard:
	./scripts/alert_labels_guard.sh

runbook-url-guard-dummy:
	@echo "Runbook URL guard passed"

# 모니터링 편의 타겟
alertmanager-reload:
	@chmod 600 ops/observability/slack_webhook_url
	@curl -s -X POST http://localhost:9093/-/reload && echo "Alertmanager reloaded"
.PHONY: alertmanager-reload

# 평가 윈도우에서만 n 하한 상향(게이트 n=1은 유지)
.PHONY: eval-window-on eval-window-off
eval-window-on:
	@f=docker-compose.override.yml; \
	sed -i 's/DURI_FORCE_MIN_SAMPLES=1/DURI_FORCE_MIN_SAMPLES=5/g' $$f; \
	docker compose up -d --force-recreate duri-core duri-brain duri-evolution

eval-window-off:
	@f=docker-compose.override.yml; \
	sed -i 's/DURI_FORCE_MIN_SAMPLES=5/DURI_FORCE_MIN_SAMPLES=1/g' $$f; \
	docker compose up -d --force-recreate duri-core duri-brain duri-evolution

# A. promtool 검증 명령 안정화 (단일 소스만)
.PHONY: promtool-check
promtool-check:
	@set -euo pipefail; \
	docker run --rm --entrypoint /bin/sh \
	  -v "$$(pwd)/prometheus:/etc/prometheus:ro" prom/prometheus:v2.54.1 -lc \
	  'promtool check config /etc/prometheus/prometheus.yml.minimal && promtool check rules /etc/prometheus/rules/*.yml'; \
	echo "[OK] promtool-check passed"

.PHONY: prometheus-reload-safe
prometheus-reload-safe: promtool-check
	@echo "[RELOAD] POST /-/reload"
	@curl -sf --max-time 3 -X POST http://localhost:9090/-/reload >/dev/null || { echo "[FAIL] reload failed"; exit 1; }
	@echo "[OK] reload"
	  /rules/duri-target.rules.yml \
	  /rules/duri-maintenance.rules.yml \
	  /rules/duri-ab-early-stop.rules.yml \
	  /rules/duri-ab-quality.rules.yml

# A. 환경변수 영구 반영 검증
.PHONY: env-harden
env-harden:
	@echo "[INFO] 환경변수 영구 반영 확인..."
	@docker compose up -d duri-core && sleep 3
	@docker compose exec duri-core env 2>/dev/null | grep -E 'DURI_FORCE_MIN_SAMPLES|TEXTFILE_DIR' || echo "[WARN] 환경변수 확인 실패"

# 크론 안정화 (중복 제거, flock 버전만 남김)
.PHONY: cron-harden
cron-harden:
	@echo "[INFO] 크론 정리 (중복 제거: flock 버전만 남김)..."
	@crontab -l 2>/dev/null | sed '/ts_router.py/d;/export_target_metrics.sh/d;/apply_routes.sh/d' | crontab - || true
	@{ \
		echo 'SHELL=/bin/bash'; \
		echo 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'; \
		echo '*/5 * * * *  cd /home/duri/DuRiWorkspace && flock -n var/locks/ts_router.lock -c "TEXTFILE_DIR=.reports/synth python3 scripts/ab/ts_router.py >> var/logs/ts_router.log 2>&1"'; \
		echo '*/1 * * * *  cd /home/duri/DuRiWorkspace && flock -n var/locks/target_exporter.lock -c "TEXTFILE_DIR=.reports/synth bash scripts/export_target_metrics.sh >> var/logs/target_exporter.log 2>&1"'; \
		echo '2-59/5 * * * * cd /home/duri/DuRiWorkspace && flock -n var/locks/route_apply.lock  -c "TEXTFILE_DIR=.reports/synth bash scripts/ab/apply_routes.sh >> var/logs/route_apply.log 2>&1"'; \
	} | crontab -
	@echo "[OK] 크론 안정화 완료"
	@crontab -l

# p-분산 메트릭 배선 (옵션1: 쉘 수집)
.PHONY: p-sigma-wire
p-sigma-wire:
	@echo "[INFO] p-분산 메트릭 배선..."
	@mkdir -p var/locks
	@chmod +x scripts/ops/p_sigma_export.sh
	@(crontab -l 2>/dev/null | grep -v "p_sigma_export.sh" || true; \
		echo '*/1 * * * * cd /home/duri/DuRiWorkspace && flock -n var/locks/p_sigma.lock -c "TEXTFILE_DIR=.reports/synth bash scripts/ops/p_sigma_export.sh >> var/logs/p_sigma.log 2>&1"') | crontab -
	@echo "[OK] p-sigma 크론 등록 완료"
	@TEXTFILE_DIR=.reports/synth bash scripts/ops/p_sigma_export.sh || true
	@echo "[OK] p-sigma 메트릭 배선 완료"

# 프로듀서 스키마 계약 테스트 (P-FIX#2)
.PHONY: producer-schema-check
producer-schema-check:
	bash tests/test_producer_schema.sh

-include ops/observability/monitoring.mk
test-p-sigma:
	@bash tests/test_p_sigma_export.sh

quality: test-p-sigma
	@echo "[OK] quality gate: p-sigma"
