#!/bin/bash
set -euo pipefail

echo "=== Docker Container Health Check ==="
echo "Timestamp: $(date -Iseconds)"

# Check all containers
echo "• Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(prometheus|duri_|redis|postgres)" || echo "No relevant containers found"

# Check Prometheus specifically
echo "• Prometheus Health Check:"
if curl -sf http://localhost:9090/-/ready >/dev/null 2>&1; then
    echo "  ✓ Prometheus READY"
else
    echo "  ✗ Prometheus NOT READY"
    exit 1
fi

if curl -sf http://localhost:9090/-/healthy >/dev/null 2>&1; then
    echo "  ✓ Prometheus HEALTHY"
else
    echo "  ✗ Prometheus NOT HEALTHY"
    exit 1
fi

# Check API status
echo "• Prometheus API Status:"
if curl -sf http://localhost:9090/api/v1/status/config | jq -r '.status' 2>/dev/null | grep -q "success"; then
    echo "  ✓ API Status: SUCCESS"
else
    echo "  ✗ API Status: FAILED"
    exit 1
fi

# Check rules loaded
echo "• Prometheus Rules:"
RULES=$(curl -sf http://localhost:9090/api/v1/rules | jq -r '.data.groups[].name' 2>/dev/null | wc -l)
if [ "$RULES" -gt 0 ]; then
    echo "  ✓ Rules loaded: $RULES groups"
else
    echo "  ✗ No rules loaded"
    exit 1
fi

echo "=== All Health Checks PASSED ==="
