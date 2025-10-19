#!/usr/bin/env bash
set -Eeuo pipefail

# 스모크 체크 스크립트 (운영 스크립트에 추가 추천)
# Prometheus 기본 상태 확인 및 무중단 리로드

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
cd "$PROJECT_DIR"

echo "=== Prometheus 스모크 체크 ==="
echo "Timestamp: $(date -Is)"

# 1) 준비 상태 확인
echo -e "\n**1) Prometheus 준비 상태:**"
if curl -sf http://localhost:9090/-/ready >/dev/null 2>&1; then
    echo "✅ Prometheus 준비 완료"
else
    echo "❌ Prometheus 준비 미완료"
    exit 1
fi

# 2) 룰 로드 확인 (알람 활성화 여부와 무관)
echo -e "\n**2) 룰 로드 상태:**"
RULES_COUNT=$(curl -sf http://localhost:9090/api/v1/rules | jq '.data.groups | length' 2>/dev/null || echo "0")
if [ "$RULES_COUNT" -gt 0 ]; then
    echo "✅ 룰 로드 완료 ($RULES_COUNT 그룹)"
else
    echo "❌ 룰 로드 실패"
    exit 1
fi

# 3) 기본 up 지표 확인 (샘플 쿼리)
echo -e "\n**3) 기본 지표 확인:**"
UP_COUNT=$(curl -sf "http://localhost:9090/api/v1/query?query=up" | jq '.data.result | length' 2>/dev/null || echo "0")
if [ "$UP_COUNT" -gt 0 ]; then
    echo "✅ 기본 지표 정상 ($UP_COUNT 타겟)"
else
    echo "❌ 기본 지표 없음"
    exit 1
fi

# 4) 무중단 리로드 테스트 (옵션)
if [[ "${1:-}" == "--reload" ]]; then
    echo -e "\n**4) 무중단 리로드 테스트:**"
    if curl -X POST -sf http://localhost:9090/-/reload >/dev/null 2>&1; then
        echo "✅ 리로드 성공"
    else
        echo "❌ 리로드 실패"
        exit 1
    fi
fi

echo -e "\n=== 스모크 체크 완료 ==="
