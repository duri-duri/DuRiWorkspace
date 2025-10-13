#!/usr/bin/env bash
set -euo pipefail
echo "== Prometheus rules verify (prod) =="
promtool check rules prometheus/rules/*.rules.yml
echo "== Prometheus rules unit test (test-only rules) =="
promtool test rules tests/prom_rules/quality_alerts.test.yml
echo "OK"
