# ops/observability/monitoring.mk
ifndef MONITORING_HELPERS_INCLUDED
ALERTMANAGER_CONTAINER ?= alertmanager
MONITORING_HELPERS_INCLUDED := 1

.PHONY: alertmanager-reload-monitoring clean-submodules-monitoring status-monitoring monitoring-check alertmanager-apply monitoring-help secret-perms-secure secret-perms-relaxed alertmanager-apply-secure

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
	@printf "Webhook file: "; stat -c '%a %n' ops/observability/slack_webhook_url 2>/dev/null || echo "missing"

monitoring-check:
	@f=ops/observability/slack_webhook_url; \
	test -f $$f || { echo "❌ $$f not found"; exit 1; }; \
	perm=$$(stat -c "%a" $$f 2>/dev/null || echo 000); \
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
	if command -v docker >/dev/null 2>&1 && docker ps --format "{{.Names}}" | grep -q "^$(ALERTMANAGER_CONTAINER)$$"; then \
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
	@f=ops/observability/slack_webhook_url; \
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
	@f=ops/observability/slack_webhook_url; \
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

# 운영용 "안전 적용" 번들 타겟
alertmanager-apply-secure: secret-perms-secure
	@$(MAKE) --no-print-directory monitoring-check
	@$(MAKE) --no-print-directory alertmanager-reload-monitoring
	@echo "✅ secure apply done"

monitoring-help:
	@echo "Monitoring targets:"
	@echo "  status-monitoring               - Check system status"
	@echo "  alertmanager-reload-monitoring  - Secure webhook file + reload AM"
	@echo "  clean-submodules-monitoring     - Clean submodules (safe)"
	@echo "  monitoring-check                 - Check webhook format & permissions"
	@echo "  alertmanager-apply              - Check + reload Alertmanager"
	@echo "  alertmanager-apply-secure        - Secure perms + check + reload"
	@echo "  secret-perms-secure             - Set secure mode (600, owner 65534)"
	@echo "  secret-perms-relaxed            - Set relaxed mode (644, owner current user)"
	@echo ""
	@echo "Usage examples:"
	@echo "  make monitoring-check                    # Check webhook & AM health"
	@echo "  make alertmanager-apply                   # Safe reload with checks"
	@echo "  make VERBOSE=1 clean-submodules-monitoring # Verbose submodule clean"
	@echo "  make secret-perms-secure                 # Switch to secure mode"
	@echo "  make secret-perms-relaxed                # Switch to relaxed mode"

endif
