# ops/observability/monitoring.mk
ifndef MONITORING_HELPERS_INCLUDED
MONITORING_HELPERS_INCLUDED := 1

.PHONY: alertmanager-reload-monitoring clean-submodules-monitoring status-monitoring monitoring-check alertmanager-apply monitoring-help

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
	perm=$$(stat -c '%a' $$f 2>/dev/null || echo 000); \
	[ "$$perm" = "644" ] || { echo "❌ $$f perm $$perm (need 644)"; exit 1; }; \
	url=$$(cat $$f); \
	case "$$url" in \
	  https://hooks.slack.com/services/*) echo "✅ webhook format OK";; \
	  *) echo "❌ invalid webhook format"; exit 1;; \
	esac; \
	curl -fsS http://localhost:9093/-/healthy >/dev/null && echo "✅ Alertmanager healthy"

alertmanager-apply: monitoring-check
	@chmod 600 ops/observability/slack_webhook_url 2>/dev/null || true
	@curl -fsS -X POST http://localhost:9093/-/reload >/dev/null && echo "🔁 Alertmanager reloaded"

monitoring-help:
	@echo "Monitoring targets:"
	@echo "  status-monitoring               - Check system status"
	@echo "  alertmanager-reload-monitoring  - Secure webhook file + reload AM"
	@echo "  clean-submodules-monitoring     - Clean submodules (safe)"
	@echo "  monitoring-check                 - Check webhook format & permissions"
	@echo "  alertmanager-apply              - Check + reload Alertmanager"
	@echo ""
	@echo "Usage examples:"
	@echo "  make monitoring-check                    # Check webhook & AM health"
	@echo "  make alertmanager-apply                   # Safe reload with checks"
	@echo "  make VERBOSE=1 clean-submodules-monitoring # Verbose submodule clean"

endif
