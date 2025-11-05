#!/usr/bin/env bash
# L4.0 스크립트 함수 의존성 제거 (비대화형 안전)
# Usage: bash scripts/evolution/fix_script_wrapper_deps.sh
# 목적: 모든 스크립트에서 cold-* 함수 호출을 래퍼 바이너리로 교체

set -euo pipefail

echo "=== L4.0 스크립트 함수 의존성 제거 ==="
echo ""

WRAPPER_BASE="${HOME}/.local/bin"

# 교체할 함수 목록
declare -A REPLACEMENTS=(
    ["cold-run"]="${WRAPPER_BASE}/cold_run"
    ["cold-status"]="${WRAPPER_BASE}/cold_status"
    ["cold-log"]="${WRAPPER_BASE}/cold_log"
    ["cold-hash"]="${WRAPPER_BASE}/cold_hash"
)

# 수정 대상 파일 찾기
TARGET_FILES=(
    "scripts/evolution/coldsync_immediate_check.sh"
    "scripts/evolution/coldsync_recovery.sh"
    "scripts/evolution/finalize_l4_hardening.sh"
    "scripts/evolution/fix_service_unit.sh"
    "scripts/evolution/fix_atomic_install.sh"
    "scripts/evolution/coldsync_hardening_optional.sh"
)

echo "1. 스크립트 함수 호출을 래퍼로 교체:"
for FILE in "${TARGET_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        BACKUP="${FILE}.bak.$(date +%s)"
        cp -a "$FILE" "$BACKUP"
        
        MODIFIED=false
        for FUNC in "${!REPLACEMENTS[@]}"; do
            WRAPPER="${REPLACEMENTS[$FUNC]}"
            # cold-run → ${HOME}/.local/bin/cold_run 패턴 교체
            if grep -q "\b${FUNC}\b" "$FILE"; then
                # 함수 호출만 교체 (함수 정의는 유지)
                sed -i "s|\b${FUNC}\b|${WRAPPER}|g" "$FILE"
                MODIFIED=true
            fi
        done
        
        if [ "$MODIFIED" = true ]; then
            echo "  ✅ $FILE 수정 완료"
        else
            echo "  ⚠️  $FILE 함수 호출 없음 (건너뜀)"
            rm -f "$BACKUP"
        fi
    else
        echo "  ⚠️  $FILE 없음 (건너뜀)"
    fi
done
echo ""

echo "2. 교체 확인:"
for FILE in "${TARGET_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        for FUNC in "${!REPLACEMENTS[@]}"; do
            if grep -q "\b${FUNC}\b" "$FILE"; then
                echo "  ⚠️  $FILE에 여전히 ${FUNC} 함수 호출 존재"
            fi
        done
    fi
done
echo ""

echo "=== 함수 의존성 제거 완료 ==="
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/coldsync_immediate_check.sh"

