SUDO ?= sudo -n
SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.PHONY: eval gate smoke clean k-sweep archive rollup smoke-preview help shellcheck metrics metrics-dashboard metrics-watch

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

status-shadow:
	@$(SUDO) systemctl --no-pager --full status duri-rag-eval duri-pr-gate duri-rag-eval-tuned | sed -n '1,40p'

cleanup-docker:
	@echo "🧹 도커 네트워크 잔류 방지"
	@bash scripts/cleanup_docker.sh

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
