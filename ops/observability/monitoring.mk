.PHONY: alertmanager-reload-monitoring clean-submodules-monitoring status-monitoring

alertmanager-reload-monitoring:  # Secure webhook file and reload Alertmanager
	@chmod 600 ops/observability/slack_webhook_url 2>/dev/null || true
	@curl -s -X POST http://localhost:9093/-/reload >/dev/null && echo "Alertmanager reloaded ✅"

clean-submodules-monitoring:     # Clean submodule changes (ignore nested errors)
	@echo "Cleaning submodules (discard local changes)..."
	@# recursive OFF + 전체 에러 무시로 nested submodule 문제 회피
	@git -c submodule.recurse=false submodule foreach \
	  'git restore --staged . || true; git checkout -- . || true; git clean -fdx || true' || true
	@echo "Done."

status-monitoring:               # Check system status (jq optional)
	@echo "=== DuRi Workspace Status ==="
	@printf "Prometheus: "; curl -s http://localhost:9090/-/ready || true; echo
	@printf "Alertmanager: "; curl -s http://localhost:9093/-/healthy || true; echo
	@printf "Grafana: "
	@curl -s http://localhost:3000/api/health >/tmp/grafana_health.json 2>/dev/null || true; \
	if command -v jq >/dev/null 2>&1; then \
	  jq -r '.database + " - " + .version' /tmp/grafana_health.json || echo "Not ready"; \
	else \
	  grep -q '"database":"ok"' /tmp/grafana_health.json && echo "ok" || echo "Not ready"; \
	fi
	@printf "Targets: "
	@curl -s http://localhost:9090/api/v1/targets >/tmp/targets.json 2>/dev/null || true; \
	if command -v jq >/dev/null 2>&1; then \
	  jq '.data.activeTargets | length' /tmp/targets.json; \
	else \
	  grep -o '"health"' /tmp/targets.json | wc -l | tr -d ' ' || echo "n/a"; \
	fi
	@printf "Webhook file: "; stat -c '%a %n' ops/observability/slack_webhook_url 2>/dev/null || echo "missing"
