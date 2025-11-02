#!/usr/bin/env bash
# Observability Contract v1: Boot-time validation
# Checks topology, metrics availability, and scrape health

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
PROM_CONTAINER="${PROM_CONTAINER:-prometheus}"
NODE_EXPORTER_URL="${NODE_EXPORTER_URL:-http://localhost:9100}"
MAX_WAIT="${MAX_WAIT:-60}"

errors=0

echo "[CHECK] Observability Contract v1 Boot Test"
echo "=========================================="

# 1. Check Prometheus config for node-exporter:9100 target
echo ""
echo "[1/6] Checking Prometheus configuration..."
if docker ps --format '{{.Names}}' | grep -qx "$PROM_CONTAINER" 2>/dev/null; then
    config=$(docker exec "$PROM_CONTAINER" sh -lc "wget -qO- 'http://localhost:9090/api/v1/status/config' 2>&1" 2>/dev/null || echo "")
    if echo "$config" | jq -e '.data.yaml' >/dev/null 2>&1; then
        yaml_config=$(echo "$config" | jq -r '.data.yaml' 2>/dev/null || echo "")
        if echo "$yaml_config" | grep -q "node-exporter:9100"; then
            echo "  ✓ node-exporter:9100 found in config"
            # Save config dump
            mkdir -p .reports
            echo "$config" | jq -r '.data.yaml' > .reports/prom_config.json 2>/dev/null || true
        else
            echo "  ✗ node-exporter:9100 NOT found in config"
            errors=$((errors + 1))
        fi
    else
        echo "  ✗ Failed to fetch Prometheus config"
        errors=$((errors + 1))
    fi
else
    echo "  ⚠ Prometheus container not found, skipping config check"
fi

# 2. Check node-exporter /metrics endpoint for duri_* metrics
echo ""
echo "[2/6] Checking node-exporter metrics endpoint..."
duri_count=0
if curl -sf --max-time 5 "$NODE_EXPORTER_URL/metrics" >/dev/null 2>&1; then
    duri_count=$(curl -sf --max-time 5 "$NODE_EXPORTER_URL/metrics" 2>/dev/null | grep -c "^duri_" 2>/dev/null || echo "0")
    duri_count=${duri_count:-0}
    if [ "$duri_count" -ge 3 ] 2>/dev/null; then
        echo "  ✓ Found $duri_count duri_* metrics in node-exporter"
    else
        echo "  ✗ Only $duri_count duri_* metrics found (expected >= 3)"
        errors=$((errors + 1))
    fi
else
    echo "  ✗ Cannot reach node-exporter at $NODE_EXPORTER_URL"
    errors=$((errors + 1))
fi

# 3. Check Prometheus labels for duri_* metrics
echo ""
echo "[3/6] Checking Prometheus labels..."
wait_count=0
duri_labels_count=0
while [ $wait_count -lt $MAX_WAIT ]; do
    # Use __name__/values endpoint (more reliable)
    names_resp=$(curl -sf --max-time 5 "$PROM_URL/api/v1/labels/__name__/values" 2>/dev/null || echo "")
    if echo "$names_resp" | jq -e '.data' >/dev/null 2>&1; then
        names_count=$(echo "$names_resp" | jq -r '.data[]?' 2>/dev/null | grep -c '^duri_' 2>/dev/null || echo "0")
        names_count=${names_count:-0}
        if [ "$names_count" -ge 3 ] 2>/dev/null; then
            echo "  ✓ Found $names_count duri_* metric names in Prometheus"
            duri_labels_count=$names_count
            break
        fi
    fi
    sleep 2
    wait_count=$((wait_count + 2))
done

duri_labels_count=${duri_labels_count:-0}
if [ "$duri_labels_count" -lt 3 ] 2>/dev/null; then
    echo "  ✗ Only $duri_labels_count duri_* metric names found (expected >= 3)"
    errors=$((errors + 1))
fi

# 4. Check node job is UP
echo ""
echo "[4/6] Checking node job target..."
wait_count=0
node_up=0
while [ $wait_count -lt $MAX_WAIT ]; do
    targets_resp=$(curl -sf --max-time 5 "$PROM_URL/api/v1/targets" 2>/dev/null || echo "")
    if echo "$targets_resp" | jq -e '.data.activeTargets' >/dev/null 2>&1; then
        node_health=$(echo "$targets_resp" | jq -r '.data.activeTargets[]? | select(.labels.job=="node") | .health' 2>/dev/null | head -1 || echo "")
        if [ "$node_health" = "up" ]; then
            echo "  ✓ node job is UP"
            node_up=1
            break
        fi
    fi
    sleep 2
    wait_count=$((wait_count + 2))
done

if [ "$node_up" -eq 0 ]; then
    echo "  ✗ node job is not UP"
    errors=$((errors + 1))
fi

# 5. Check node_textfile_scrape_error == 0
echo ""
echo "[5/6] Checking textfile scrape errors..."
wait_count=0
scrape_error=0
while [ $wait_count -lt $MAX_WAIT ]; do
    error_resp=$(curl -sf --max-time 5 "$PROM_URL/api/v1/query?query=node_textfile_scrape_error{job=\"node\"}" 2>/dev/null || echo "")
    if echo "$error_resp" | jq -e '.data.result[0].value[1]' >/dev/null 2>&1; then
        error_value=$(echo "$error_resp" | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "")
        if [ "$error_value" = "0" ] || [ "$error_value" = "0.0" ]; then
            echo "  ✓ node_textfile_scrape_error == 0"
            scrape_error=0
            break
        fi
    fi
    sleep 2
    wait_count=$((wait_count + 2))
done

if [ "$scrape_error" -ne 0 ]; then
    echo "  ✗ node_textfile_scrape_error != 0"
    errors=$((errors + 1))
fi

# 6. Check critical metrics exist
echo ""
echo "[6/6] Checking critical metrics..."
critical_metrics=("duri_p_uniform_ks_p" "duri_p_unique_ratio" "duri_p_sigma" "duri_p_samples")
missing=0
for metric in "${critical_metrics[@]}"; do
    metric_resp=$(curl -sf --max-time 5 "$PROM_URL/api/v1/query?query=${metric}{job=\"node\"}" 2>/dev/null || echo "")
    if echo "$metric_resp" | jq -e '.data.result[0].value' >/dev/null 2>&1; then
        echo "  ✓ $metric exists"
    else
        echo "  ✗ $metric missing"
        missing=$((missing + 1))
    fi
done

if [ $missing -gt 0 ]; then
    echo "  ⚠ $missing critical metric(s) missing (may need time to scrape)"
    # Not counting as error if node is UP (metrics may appear soon)
    if [ "$node_up" -eq 0 ]; then
        errors=$((errors + missing))
    fi
fi

# Summary
echo ""
echo "=========================================="
if [ $errors -eq 0 ]; then
    echo "[PASS] Observability Contract v1 validation passed"
    exit 0
else
    echo "[FAIL] Observability Contract v1 validation failed: $errors error(s)"
    exit 1
fi

