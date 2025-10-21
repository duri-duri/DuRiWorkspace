SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

# 리포지토리 루트 고정

# ----- Monitoring helper targets (non-invasive) -----
.PHONY: alertmanager-reload-monitoring clean-submodules-monitoring status-monitoring

alertmanager-reload-monitoring:
	@chmod 600 ops/observability/slack_webhook_url
	@curl -s -X POST http://localhost:9093/-/reload >/dev/null && 	  echo "Alertmanager reloaded ✅"

clean-submodules-monitoring:
	@echo "Cleaning submodules (discard local changes)..."
	@git submodule foreach --recursive 'git restore --staged . || true; git checkout -- . || true; git clean -fdx || true'
	@echo "Done."

status-monitoring:
	@echo "=== DuRi Workspace Status ==="
	@printf "Prometheus: "; curl -s http://localhost:9090/-/ready || true; echo
	@printf "Alertmanager: "; curl -s http://localhost:9093/-/healthy || true; echo
	@printf "Grafana: "; curl -s http://localhost:3000/api/health 2>/dev/null | jq -r '.database + " - " + .version' 2>/dev/null || echo "Not ready"
	@printf "Targets: "; curl -s http://localhost:9090/api/v1/targets 2>/dev/null | jq '.data.activeTargets | length' 2>/dev/null || echo "n/a"
	@printf "Webhook file: "; stat -c '%a %n' ops/observability/slack_webhook_url 2>/dev/null || echo "missing"
