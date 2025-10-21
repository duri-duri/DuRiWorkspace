# ops/observability/monitoring.mk
ifndef MONITORING_HELPERS_INCLUDED
MONITORING_HELPERS_INCLUDED := 1

.PHONY: alertmanager-reload-monitoring clean-submodules-monitoring status-monitoring

alertmanager-reload-monitoring:
	@chmod 600 ops/observability/slack_webhook_url 2>/dev/null || true
	@curl -s -X POST http://localhost:9093/-/reload >/dev/null && echo "Alertmanager reloaded ✅"

clean-submodules-monitoring:
	@echo "Cleaning submodules (discard local changes)..."
	@# recursive OFF + 전체 에러 무시로 nested submodule 문제 회피
	@git -c submodule.recurse=false submodule foreach 'git restore --staged . || true; git checkout -- . || true; git clean -fdx || true' || true
	@echo "Done."

status-monitoring:
	@echo "=== DuRi Workspace Status ==="
	@printf "Prometheus: "; curl -s http://localhost:9090/-/ready || true; echo
	@printf "Alertmanager: "; curl -s http://localhost:9093/-/healthy || true; echo
	@printf "Grafana: "; curl -s http://localhost:3000/api/health 2>/dev/null | jq -r '.database + " - " + .version' 2>/dev/null || echo "Not ready"
	@printf "Targets: "; curl -s http://localhost:9090/api/v1/targets 2>/dev/null | jq '.data.activeTargets | length' 2>/dev/null || echo "n/a"
	@printf "Webhook file: "; stat -c '%a %n' ops/observability/slack_webhook_url 2>/dev/null || echo "missing"

endif
