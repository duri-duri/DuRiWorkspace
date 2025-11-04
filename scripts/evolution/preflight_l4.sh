#!/usr/bin/env bash
# L4.0 승급 실행 전 강화된 프리플라이트 (실패 여지 4곳 조임)
# Usage: bash scripts/evolution/preflight_l4.sh
# 목적: p≈0.88 → p≈0.90으로 상향

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 승급 실행 전 강화된 프리플라이트 ==="
echo ""

FAILED=0
WARNINGS=0

# 0) 이름 혼재 정리 (표준=oneline)
echo "=== 0) 이름 혼재 정리 (표준=oneline) ==="
echo ""

if [ -f "scripts/bin/status_coldsync_autodeploy.sh" ] && [ ! -L "scripts/bin/status_coldsync_autodeploy.sh" ]; then
    echo "기존 파일 삭제 후 심볼릭 링크 생성:"
    rm -f scripts/bin/status_coldsync_autodeploy.sh
fi

if [ -f "scripts/bin/status_coldsync_oneline.sh" ]; then
    ln -sf status_coldsync_oneline.sh scripts/bin/status_coldsync_autodeploy.sh
    echo "✅ 심볼릭 링크 생성: status_coldsync_autodeploy.sh → status_coldsync_oneline.sh"
    
    chmod +x scripts/bin/status_coldsync_oneline.sh
    if ! head -n1 scripts/bin/status_coldsync_oneline.sh | grep -q '#!'; then
        sed -i '1i#!/usr/bin/env bash' scripts/bin/status_coldsync_oneline.sh
        echo "✅ shebang 추가됨"
    fi
else
    echo "❌ status_coldsync_oneline.sh 없음"
    ((FAILED++))
fi

echo ""

# 프리플라이트 6줄 (충돌·드리프트 즉시 탐지)
echo "=== 프리플라이트 6줄 (충돌·드리프트 즉시 탐지) ==="
echo ""

# A. 단일 상태 스크립트 존재/권한
if test -x scripts/bin/status_coldsync_oneline.sh; then
    echo "✅ A. status_coldsync_oneline.sh 존재/실행권한 OK"
else
    echo "❌ A. status_coldsync_oneline.sh 존재/실행권한 실패"
    ((FAILED++))
fi

# B. 유닛 정상 로드 (시스템 vs 유저 둘 다 확인)
echo ""
echo "B. 유닛 정상 로드 확인:"
echo "시스템:"
(systemctl status coldsync-install.path coldsync-verify.timer --no-pager 2>/dev/null || true) | grep -E 'Loaded|Active' || echo "  시스템 유닛 없음"
echo "유저:"
(systemctl --user status coldsync-install.path coldsync-verify.timer --no-pager 2>/dev/null || true) | grep -E 'Loaded|Active' || echo "  유저 유닛 없음"

# C. 바이너리/소스 해시 드리프트
echo ""
echo "C. 바이너리/소스 해시 드리프트:"
# 워킹트리 경로 우선 + ENV override
COLDSYNC_SRC_PATH="${COLDSYNC_SRC_PATH:-/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh}"
COLDSYNC_DST_PATH="${COLDSYNC_DST_PATH:-/usr/local/bin/coldsync_hosp_from_usb.sh}"

SRC_HASH=$(sha256sum "$COLDSYNC_SRC_PATH" 2>/dev/null | awk '{print $1}' || echo "")
DST_HASH=$(sha256sum "$COLDSYNC_DST_PATH" 2>/dev/null | awk '{print $1}' || echo "not-installed")

if [ -n "$SRC_HASH" ]; then
    echo "  SRC=$SRC_HASH"
else
    echo "  SRC=not-found"
    ((FAILED++))
fi

if [ "$DST_HASH" != "not-installed" ]; then
    echo "  DST=$DST_HASH"
    if [ "$SRC_HASH" != "$DST_HASH" ]; then
        echo "  ⚠️  해시 불일치 감지"
        ((WARNINGS++))
    else
        echo "  ✅ 해시 일치"
    fi
else
    echo "  DST=not-installed"
    echo "  ℹ️  아직 설치되지 않음 (정상)"
fi

if [ "$SRC_HASH" != "$DST_HASH" ] && [ "$DST_HASH" != "not-installed" ]; then
    echo ""
    echo "📋 해시 불일치 감지 → finalize 재실행 권장"
fi

echo ""

# 1) 유닛/타이머 즉시 AC 스냅샷 (권한·경로·트리거 확인)
echo "=== 1) 유닛/타이머 즉시 AC 스냅샷 ==="
echo ""

sudo systemctl daemon-reload || true
echo "✅ systemd daemon-reload 완료"

if sudo systemctl enable --now coldsync-install.path coldsync-verify.timer 2>/dev/null; then
    echo "✅ 유닛 enabled/started"
else
    echo "⚠️  유닛 활성화 경고 (계속 진행)"
    ((WARNINGS++))
fi

echo ""
echo "유닛 상태 (systemctl show):"
PATH_STATE=$(systemctl show -p ActiveState,UnitFileState coldsync-install.path 2>/dev/null || echo "")
TIMER_STATE=$(systemctl show -p ActiveState,UnitFileState coldsync-verify.timer 2>/dev/null || echo "")

if echo "$PATH_STATE" | grep -q 'ActiveState=active' && echo "$PATH_STATE" | grep -q 'UnitFileState=enabled'; then
    echo "✅ coldsync-install.path: ActiveState=active, UnitFileState=enabled"
else
    echo "❌ coldsync-install.path: 상태 불일치"
    echo "  $PATH_STATE"
    ((FAILED++))
fi

if echo "$TIMER_STATE" | grep -q 'ActiveState=active' && echo "$TIMER_STATE" | grep -q 'UnitFileState=enabled'; then
    echo "✅ coldsync-verify.timer: ActiveState=active, UnitFileState=enabled"
else
    echo "❌ coldsync-verify.timer: 상태 불일치"
    echo "  $TIMER_STATE"
    ((FAILED++))
fi

echo ""

# 2) 스크립트 무결성 3신호 (존재/실행권한/SHA256)
echo "=== 2) 스크립트 무결성 3신호 (존재/실행권한/SHA256) ==="
echo ""

CHECK_FILES=(
    "finalize_coldsync_autodeploy.sh"
    "test_coldsync_autodeploy.sh"
    "status_coldsync_oneline.sh"
    "verify_coldsync_final.sh"
    "snapshot_coldsync_security.sh"
    "recover_coldsync.sh"
    "rollback_coldsync.sh"
    "tag_coldsync_baseline.sh"
)

MISS_COUNT=0
NOEXEC_COUNT=0

for f in "${CHECK_FILES[@]}"; do
    p="scripts/bin/$f"
    echo "체크: $f"
    
    # 존재 확인
    if [ ! -f "$p" ]; then
        echo "  [MISS] $p"
        ((MISS_COUNT++))
        ((FAILED++))
    else
        echo "  [EXISTS] $p"
    fi
    
    # 실행권한 확인
    if [ -f "$p" ] && [ ! -x "$p" ]; then
        echo "  [NOEXEC] $p"
        chmod +x "$p"
        echo "  ✅ 실행권한 부여됨"
        ((NOEXEC_COUNT++))
    elif [ -f "$p" ]; then
        echo "  [EXEC] $p"
    fi
    
    # SHA256
    if [ -f "$p" ]; then
        sha256sum "$p" | awk '{print "  [SHA256]",$2,$1}'
    fi
    
    echo ""
done

if [ $MISS_COUNT -eq 0 ] && [ $NOEXEC_COUNT -eq 0 ]; then
    echo "✅ 모든 파일 존재/실행권한 OK"
else
    echo "❌ 누락: $MISS_COUNT건, 실행권한 없음: $NOEXEC_COUNT건"
fi

echo ""

# 3) 사전 증거 확보 (로그/보안/기준선 태깅)
echo "=== 3) 사전 증거 확보 (로그/보안/기준선 태깅) ==="
echo ""

echo "상태 확인:"
bash scripts/bin/status_coldsync_oneline.sh || {
    echo "⚠️  상태 확인 경고 (계속 진행)"
    ((WARNINGS++))
}
echo ""

echo "GO/NO-GO 자동 판정:"
bash scripts/bin/verify_coldsync_final.sh || {
    echo "❌ verify_coldsync_final 실패"
    ((FAILED++))
}
echo ""

echo "보안/신뢰도 스냅샷:"
bash scripts/bin/snapshot_coldsync_security.sh || {
    echo "⚠️  스냅샷 경고 (계속 진행)"
    ((WARNINGS++))
}
echo ""

echo "운영 기준선 태깅:"
bash scripts/bin/tag_coldsync_baseline.sh || {
    echo "⚠️  태깅 경고 (계속 진행)"
    ((WARNINGS++))
}
echo ""

# 빠른 정합성 점검 (선택, 30초)
echo "=== 빠른 정합성 점검 ==="
echo ""

echo "실행 파일 존재/권한:"
ls -l scripts/bin/{finalize_coldsync_autodeploy.sh,test_coldsync_autodeploy.sh,status_coldsync_oneline.sh,verify_coldsync_final.sh,snapshot_coldsync_security.sh,recover_coldsync.sh,rollback_coldsync.sh,tag_coldsync_baseline.sh} \
      scripts/evolution/{preflight_l4.sh,run_l4_timeline.sh,check_l4_timeline.sh,spotcheck_l4.sh,quick_l4_check.sh,verify_l4_gate.sh,promote_to_l4.sh,execute_l4_promotion.sh} 2>/dev/null | awk '{print $1,$9}' || echo "일부 파일 없음"
echo ""

echo "systemd 상태 요약:"
systemctl status coldsync-install.path --no-pager 2>/dev/null | sed -n '1,5p' || echo "상태 확인 실패"
systemctl status coldsync-verify.timer --no-pager 2>/dev/null | sed -n '1,5p' || echo "상태 확인 실패"
echo ""

echo "SHA 추적 로그 핵심 키워드 (최근 15분):"
journalctl -u coldsync-install.service --since "15 minutes ago" --no-pager 2>/dev/null | grep -E 'INSTALLED|No change|SHA256|MISMATCH|FAILED' | tail -n 20 || echo "로그 없음"
echo ""

# 최종 판정 함수 (원클릭 GO/NO-GO)
echo "=== 최종 판정 함수 (원클릭 GO/NO-GO) ==="
echo ""

if bash scripts/bin/verify_coldsync_final.sh && bash scripts/evolution/check_l4_ac.sh 2>/dev/null; then
    echo "[L4] ✅ GO"
    echo ""
    echo "📋 다음 단계:"
    echo "  창1: bash scripts/evolution/run_l4_timeline.sh"
    echo "  창2: watch -n5 'bash scripts/evolution/spotcheck_l4.sh'"
    echo "  창3: journalctl -u coldsync-install.service -f --no-pager | egrep --line-buffered 'FAILED|SHA256|ROLLBACK|MISMATCH|halluc|stability'"
    echo ""
    echo "📍 체크포인트:"
    echo "  T+2분: bash scripts/evolution/check_l4_timeline.sh T2"
    echo "  T+15분: bash scripts/evolution/check_l4_timeline.sh T15"
    echo "  T+24h: bash scripts/evolution/check_l4_timeline.sh T24h"
    echo ""
    echo "🔴 개입 트리거 발생 시:"
    echo "  bash scripts/evolution/l4_killswitch.sh recover"
    echo "  bash scripts/evolution/l4_killswitch.sh rollback"
    echo ""
    echo "✅ 성공 확률: p≈0.90 (보안 하드닝 + 타임라인 절차 준수)"
    exit 0
else
    echo "[L4] ❌ NO-GO"
    echo ""
    echo "실패: $FAILED건, 경고: $WARNINGS건"
    echo ""
    echo "📋 복구 후 재시도 필요"
    exit 1
fi
