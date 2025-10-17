#!/usr/bin/env bash
set -euo pipefail

echo "=== 🔒 보안/공급망 스캔 ==="

# SBOM 생성 (syft)
if command -v syft &> /dev/null; then
    echo "📦 SBOM 생성 중..."
    syft duriworkspace-duri_control:latest -o json > sbom_$(date +%Y%m%d_%H%M%S).json
    echo "✅ SBOM 생성 완료"
else
    echo "⚠️ syft가 설치되지 않음. SBOM 생성 건너뜀"
fi

# 취약성 스캔 (grype)
if command -v grype &> /dev/null; then
    echo "🔍 취약성 스캔 중..."
    grype duriworkspace-duri_control:latest -o json > vuln_scan_$(date +%Y%m%d_%H%M%S).json
    echo "✅ 취약성 스캔 완료"
else
    echo "⚠️ grype가 설치되지 않음. 취약성 스캔 건너뜀"
fi

echo "🔒 보안 스캔 완료"
