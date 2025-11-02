#!/usr/bin/env bash
# promtool 검증 스크립트
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== promtool 규칙 검증 ==="
echo ""

if ! command -v promtool >/dev/null 2>&1; then
    echo "[WARN] promtool 없음 (Prometheus 설치 필요)"
    echo "[INFO] promtool 설치: apt-get install prometheus-common"
    exit 0
fi

# Prometheus 규칙 파일 검증
RULES_DIR="prometheus/rules"
if [ -d "$RULES_DIR" ]; then
    for rule_file in "$RULES_DIR"/*.yml; do
        if [ -f "$rule_file" ]; then
            echo "검증 중: $rule_file"
            if promtool check rules "$rule_file" 2>&1; then
                echo "[OK] $rule_file"
            else
                echo "[FAIL] $rule_file"
                exit 1
            fi
        fi
    done
else
    echo "[WARN] 규칙 디렉터리 없음: $RULES_DIR"
fi

echo ""
echo "[OK] promtool 규칙 검증 완료"

