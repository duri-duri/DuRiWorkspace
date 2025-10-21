# Variables
WEBHOOK_FILE ?= ops/observability/slack_webhook_url

# ops/observability/monitoring.mk
ifndef MONITORING_HELPERS_INCLUDED
ALERTMANAGER_CONTAINER ?= $(shell docker ps --format '{{.Names}}' | grep -E '^alertmanager$$|^am$$' | head -n1 || echo alertmanager)
SKIP_WEBHOOK_GUARD ?= 0
MONITORING_HELPERS_INCLUDED := 1

# macOS 호환 stat 명령어
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  STAT_MODE = stat -f '%Lp'
  STAT_NAME = stat -f '%N'
else
  STAT_MODE = stat -c '%a'
  STAT_NAME = stat -c '%n'
endif

# 이식성 stat 함수(더 안전하게)
STAT_PERM = $(shell \
  if stat -f "%p" / >/dev/null 2>&1; then \
    stat -f "%p" ops/observability/slack_webhook_url | tail -c 4; \
  else \
    stat -c "%a" ops/observability/slack_webhook_url; \
  fi 2>/dev/null || echo 000)

.PHONY: alertmanager-reload-monitoring clean-submodules-monitoring status-monitoring monitoring-check alertmanager-apply monitoring-help secret-perms-secure secret-perms-relaxed alertmanager-apply-secure precommit-safe ci-smoke alertmanager-validate

alertmanager-reload-monitoring:
	@chmod 600 ops/observability/slack_webhook_url 2>/dev/null || true
	@curl -s -X POST http://localhost:9093/-/reload >/dev/null && echo "Alertmanager reloaded ✅"

clean-submodules-monitoring:
	@echo "Cleaning submodules (discard local changes)..."
	@{ \
	  git -c submodule.recurse=false submodule foreach \
	    'git restore --staged . || true; git checkout -- . || true; git clean -fdx || true' \
	    $(if $(VERBOSE),,2>/dev/null) || true; \
	} && echo "Done."

status-monitoring:
	@echo "=== DuRi Workspace Status ==="
	@printf "Prometheus: "; curl -s http://localhost:9090/-/ready || true; echo
	@printf "Alertmanager: "; curl -s http://localhost:9093/-/healthy || true; echo
	@printf "Grafana: "; curl -s http://localhost:3000/api/health 2>/dev/null | jq -r '.database + " - " + .version' 2>/dev/null || echo "Not ready"
	@printf "Targets: "; curl -s http://localhost:9090/api/v1/targets 2>/dev/null | jq '.data.activeTargets | length' 2>/dev/null || echo "n/a"
	@printf "Webhook file: "; $(STAT_MODE) ops/observability/slack_webhook_url 2>/dev/null | xargs -I{} echo "{} ops/observability/slack_webhook_url" || echo "missing"

monitoring-check:
	@f=$(WEBHOOK_FILE); \
	test -f $$f || { echo "❌ $$f not found"; exit 1; }; \
	perm=$$($(STAT_MODE) $$f 2>/dev/null || echo 000); \
	echo "ℹ️ host perm: $$perm"; \
	# 1) (선택) 형식 체크: 호스트가 읽을 수 있을 때만 수행 \
	if [ -r "$$f" ]; then \
	  if grep -q 'YOUR/SLACK/WEBHOOK' "$$f"; then \
	    [ "$(SKIP_WEBHOOK_GUARD)" = "1" ] || { echo "❌ placeholder webhook"; exit 1; }; \
	  fi; \
	  case "$$(head -c 10 $$f 2>/dev/null)" in \
	    https://hoo*) echo "✅ webhook format looks OK" ;; \
	    *) echo "⚠️ format not verified (non-fatal)" ;; \
	  esac; \
	else \
	  echo "ℹ️ host can't read (secure mode) — skipping placeholder check"; \
	fi; \
	# 2) 컨테이너 안 읽기 가능 여부(권위 체크) \
	if command -v docker >/dev/null 2>&1 && docker ps --format "{{.Names}}" | grep -q "^${ALERTMANAGER_CONTAINER}$$"; then \
	  docker exec "$(ALERTMANAGER_CONTAINER)" sh -lc "test -r /etc/alertmanager/secrets/slack_webhook_url" \
	    && echo "✅ readable in container" \
	    || { echo "❌ not readable in container"; exit 1; }; \
	else \
	  echo "ℹ️ docker AM not found → skipping in-container read test"; \
	fi; \
	# 3) AM 헬스 \
	curl -fsS --max-time 3 http://localhost:9093/-/healthy >/dev/null && echo "✅ Alertmanager healthy"

alertmanager-apply: monitoring-check
	@chmod 600 ops/observability/slack_webhook_url 2>/dev/null || true
	@curl -fsS -X POST http://localhost:9093/-/reload >/dev/null && echo "🔁 Alertmanager reloaded"

# 보안 모드: 컨테이너(nobody:65534)만 읽기(600)
secret-perms-secure:
	@f=$(WEBHOOK_FILE); \
	test -f $$f || { echo "❌ $$f not found"; exit 1; }; \
	if sudo -n true 2>/dev/null; then \
	  sudo chown 65534:65534 $$f && sudo chmod 600 $$f; \
	else \
	  docker run --rm -v $$PWD/ops/observability:/secrets alpine \
	    sh -lc "chown 65534:65534 /secrets/slack_webhook_url && chmod 600 /secrets/slack_webhook_url"; \
	fi; \
	echo "🔒 set $$f -> owner 65534:65534, mode 600"

# 편의 모드: 호스트 사용자 읽기 가능(644)
secret-perms-relaxed:
	@f=$(WEBHOOK_FILE); \
	test -f $$f || { echo "❌ $$f not found"; exit 1; }; \
	if sudo -n true 2>/dev/null; then \
	  sudo chown $$(id -u):$$(id -g) $$f && sudo chmod 644 $$f; \
	else \
	  docker run --rm \
	    -e HOST_UID=$$(id -u) -e HOST_GID=$$(id -g) \
	    -v $$PWD/ops/observability:/secrets alpine \
	    sh -lc "chown \$$HOST_UID:\$$HOST_GID /secrets/slack_webhook_url && chmod 644 /secrets/slack_webhook_url"; \
	fi; \
	echo "🟢 set $$f -> owner $$(id -un):$$(id -gn), mode 644"

# Alertmanager 설정 문법 검증
alertmanager-validate:
	@if docker exec "$(ALERTMANAGER_CONTAINER)" sh -lc 'command -v amtool >/dev/null'; then \
	  docker exec "$(ALERTMANAGER_CONTAINER)" amtool check-config /etc/alertmanager/alertmanager.yml || exit 1; \
	else \
	  echo "ℹ️ amtool not found; skipping syntax check"; \
	fi

# 운영용 "안전 적용" 번들 타겟
alertmanager-apply-secure: secret-perms-secure alertmanager-validate
	@$(MAKE) --no-print-directory monitoring-check
	@$(MAKE) --no-print-directory alertmanager-reload-monitoring
	@echo "✅ secure apply done"

monitoring-help:
	@echo "Monitoring targets:"
	@echo "  monitoring-check                 - Check container readability & AM health (format check skipped in secure/CI)"
	@echo "  status-monitoring                - Print Prometheus/Alertmanager/Grafana health and targets"
	@echo "  alertmanager-reload-monitoring   - Reload Alertmanager safely"
	@echo "  secret-perms-relaxed             - Set webhook perms for local edits (644)"
	@echo "  alertmanager-apply-secure        - Enforce secure perms (600) and reload AM"
	@echo "  ci-smoke                         - CI smoke (green path)"
	@echo "  alertmanager-validate            - Validate Alertmanager config syntax"
	@echo ""
	@echo "Variables:"
	@echo "  ALERTMANAGER_CONTAINER=$(ALERTMANAGER_CONTAINER), SKIP_WEBHOOK_GUARD=$(SKIP_WEBHOOK_GUARD)"

# pre-commit 안전가드 타겟
precommit-safe: secret-perms-relaxed
	@echo "✅ secrets set to relaxed (644) for safe commits"

# CI 스모크 번들 타겟(1버튼 회귀)
ci-smoke:
	@$(MAKE) --no-print-directory secret-perms-relaxed
	@SKIP_WEBHOOK_GUARD=1 $(MAKE) --no-print-directory monitoring-check

endif

.PHONY: canary-alert
canary-alert:
	@echo "Sending canary alert via amtool…"
	@docker exec "${ALERTMANAGER_CONTAINER}" sh -lc \
	 'amtool --alertmanager.url=http://localhost:9093 alert add \
	    alertname=CHATGPT_CANARY severity=info \
	    summary=CanaryTest description=AutomatedCanary' \
	&& echo "✅ Canary alert sent" || { echo "❌ Failed to send canary alert"; exit 1; }
