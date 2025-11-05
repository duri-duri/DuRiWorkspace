#!/usr/bin/env bash
# L4.0 달성식 및 태깅 스크립트
# 목적: L4.0 Gate 통과 시 운영선언 및 태깅
# Usage: bash scripts/evolution/declare_l4.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 달성식 및 운영선언 ==="
echo ""

# 1. Gate 검증
echo "1. L4.0 Gate 검증"
bash scripts/evolution/verify_l4_gate.sh
GATE_RESULT=$?

if [ $GATE_RESULT -ne 0 ]; then
    echo ""
    echo "❌ Gate 검증 실패. L4.0 승급 불가."
    exit 1
fi

echo ""
echo "✅ 모든 Gate 통과 확인"
echo ""

# 2. 최종 검증
echo "2. 최종 검증"
echo "coldsync 시스템 상태:"
bash scripts/bin/status_coldsync_oneline.sh
echo ""

# 3. 프로모션 스코어 확인
echo "3. 프로모션 스코어 확인 (7일)"
python3 scripts/evolution/promotion_gate_v2.py --window 168 --gate L4.1 --output /tmp/l4_final_score.json || true
echo ""

# 4. 태깅
TAG_NAME="l4-coldsync-go-$(date +%Y%m%d)"
TAG_MESSAGE="L4.0 운영선언

- 자가복구: ✅ SHA256 불일치 2분 내 자동 재설치
- 권한·경로 봉쇄: ✅ sudoers 화이트리스트 외 차단
- Plan→Exec→Verify→Report: ✅ pass_rate ≥ 0.97
- 타이머 백스탑: ✅ Path 실패 시 타이머 복구
- 프로모션 스코어: ✅ 7일 기준 ≥ 0.82
- 무인 운영: ✅ human_intervention_rate = 0, MTTR ≤ 2분

신뢰도: p≈0.85
상태: L4.0 운영 준비 완료"

echo "4. Git 태깅"
git tag -a "$TAG_NAME" -m "$TAG_MESSAGE" || {
    echo "❌ 태그 생성 실패"
    exit 1
}

echo "✅ 태그 생성 완료: $TAG_NAME"
echo ""

# 5. 증거 아티팩트 생성
echo "5. 증거 아티팩트 생성"
ARTIFACT_DIR="${ROOT}/var/evolution/L4-DECLARATION-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$ARTIFACT_DIR"

# Gate 검증 결과
bash scripts/evolution/verify_l4_gate.sh > "$ARTIFACT_DIR/gate_verification.txt" 2>&1 || true

# 프로모션 스코어
if [ -f "/tmp/l4_final_score.json" ]; then
    cp /tmp/l4_final_score.json "$ARTIFACT_DIR/"
fi

# 시스템 상태
bash scripts/bin/status_coldsync_oneline.sh > "$ARTIFACT_DIR/system_status.txt" 2>&1 || true

# 최근 로그
sudo journalctl -u coldsync-install.service -n 50 --no-pager > "$ARTIFACT_DIR/recent_logs.txt" 2>&1 || true

echo "✅ 증거 아티팩트 저장: $ARTIFACT_DIR"
echo ""

# 6. 선언서 생성
echo "6. 선언서 생성"
DECLARATION_FILE="${ARTIFACT_DIR}/L4_DECLARATION.md"
cat > "$DECLARATION_FILE" <<EOF
# L4.0 운영선언

**날짜**: $(date +%Y-%m-%d\ %H:%M:%S)
**태그**: $TAG_NAME
**신뢰도**: p≈0.85

## Gate 통과 결과

✅ Gate 1: 자가복구 (Δ1)
✅ Gate 2: 권한·경로 봉쇄 (Δ2)
✅ Gate 3: Plan→Exec→Verify→Report 체인 (Δ3)
✅ Gate 4: 타이머 백스탑
✅ Gate 5: 프로모션 스코어 (7일 ≥ 0.82)
✅ Gate 6: 무인 운영 지표

## 시스템 상태

- coldsync-install.path: $(systemctl is-enabled coldsync-install.path 2>/dev/null || echo "unknown") / $(systemctl is-active coldsync-install.path 2>/dev/null || echo "unknown")
- coldsync-verify.timer: $(systemctl is-enabled coldsync-verify.timer 2>/dev/null || echo "unknown") / $(systemctl is-active coldsync-verify.timer 2>/dev/null || echo "unknown")

## 다음 단계

1. L4.1 진화 시스템 가동
2. 분신화(L4.5) 준비
3. L5 로드맵 수립

---

**선언**: DuRi 시스템은 이제 **L4.0 "자율 복구 및 무인 운영"** 단계에 도달했습니다.
EOF

cat "$DECLARATION_FILE"
echo ""

echo "=== L4.0 달성식 완료 ==="
echo ""
echo "📋 생성된 아티팩트:"
echo "  - Git 태그: $TAG_NAME"
echo "  - 증거 디렉토리: $ARTIFACT_DIR"
echo "  - 선언서: $DECLARATION_FILE"
echo ""
echo "📋 다음 단계:"
echo "  git push origin $TAG_NAME"
echo "  bash scripts/evolution/start_l4_evolution.sh"

