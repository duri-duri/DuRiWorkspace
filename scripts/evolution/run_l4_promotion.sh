#!/usr/bin/env bash
# L4.0 승급 실행 - 완전 자동화 (프리플라이트→실행→검증→모니터링)
# Usage: bash scripts/evolution/run_l4_promotion.sh
# 이후: 모니터링만 진행하면 됩니다

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 승급 실행 - 완전 자동화 ==="
echo ""

FAILED=0

# 0) 프리플라이트 (2분)
echo "=== 0) 프리플라이트 (2분) ==="
echo ""

echo "워킹트리 청결 확인:"
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  변경사항 있음 (계속 진행)"
    git status --short | head -5
else
    echo "✅ 워킹트리 청결"
fi
echo ""

echo "기준선 태그 확인:"
git tag --list | tail -5 || echo "태그 없음"
echo ""

echo "룰 구문 오류 체크:"
if command -v promtool >/dev/null 2>&1; then
    if promtool check rules prometheus/rules/*.yml 2>/dev/null; then
        echo "✅ promtool check rules 통과"
    else
        echo "❌ promtool check rules 실패"
        ((FAILED++))
    fi
else
    echo "⚠️  promtool 없음 (스킵)"
fi
echo ""

echo "systemd 유닛 검증:"
if systemd-analyze verify /etc/systemd/system/coldsync-install.service /etc/systemd/system/coldsync-install.path /etc/systemd/system/coldsync-verify.timer 2>/dev/null; then
    echo "✅ systemd 유닛 검증 통과"
else
    echo "⚠️  systemd 유닛 검증 경고 (계속 진행)"
fi
echo ""

echo "타이머/패스 유닛 준비:"
if systemctl is-enabled coldsync-install.path >/dev/null 2>&1 && \
   systemctl is-enabled coldsync-verify.timer >/dev/null 2>&1; then
    echo "✅ 타이머/패스 유닛 enabled"
    sudo systemctl daemon-reload || true
else
    echo "❌ 타이머/패스 유닛 미등록"
    ((FAILED++))
fi
echo ""

if [ $FAILED -gt 0 ]; then
    echo "❌ 프리플라이트 실패. 복구 권장:"
    echo "  bash scripts/bin/finalize_coldsync_autodeploy.sh"
    exit 1
fi

echo "✅ 프리플라이트 통과"
echo ""

# 1) 원클릭 승급 실행
echo "=== 1) 원클릭 승급 실행 ==="
echo ""

bash scripts/evolution/execute_l4_promotion.sh
EXEC_RESULT=$?

if [ $EXEC_RESULT -ne 0 ]; then
    echo ""
    echo "❌ 승급 실행 실패"
    echo ""
    echo "📋 실패 분기:"
    echo "  bash scripts/bin/recover_coldsync.sh"
    exit 1
fi

echo "✅ 승급 실행 완료"
echo ""

# 2) 즉시 검증 (15분 SLO)
echo "=== 2) 즉시 검증 (15분 SLO) ==="
echo ""

echo "유닛/타이머 가동:"
systemctl --no-pager status coldsync-install.path coldsync-verify.timer 2>/dev/null | grep -E 'active|enabled' || echo "상태 확인 실패"
echo ""

echo "설치 로그 키워드:"
LOG_OUTPUT=$(sudo journalctl -u coldsync-install.service -n 50 --no-pager 2>/dev/null || echo "")
if echo "$LOG_OUTPUT" | grep -qE 'INSTALLED|No change'; then
    echo "✅ INSTALLED/No change 확인됨"
else
    echo "⚠️  INSTALLED/No change 없음"
fi
echo ""

echo "게이트 결정 로그:"
find var/evolution -name "*.log" -o -name "gate.json" 2>/dev/null | head -5 | xargs grep -hE 'PROMOTE|ROLLBACK|RETRY' 2>/dev/null | tail -20 || echo "게이트 결과 없음"
echo ""

echo "SHA256 무결성:"
bash scripts/evolution/monitor_coldsync_sha.sh || true
echo ""

# 3) 증거 스냅샷 & 기준선 고정
echo "=== 3) 증거 스냅샷 & 기준선 고정 ==="
echo ""

echo "보안/신뢰도 스냅샷:"
bash scripts/bin/snapshot_coldsync_security.sh || {
    echo "⚠️  스냅샷 실패 (계속 진행)"
}
echo ""

echo "기준선 태깅:"
bash scripts/bin/tag_coldsync_baseline.sh || {
    echo "⚠️  태깅 실패 (계속 진행)"
}
echo ""

# 4) 24h 드릴 시작
echo "=== 4) 24h 드릴 시작 ==="
echo ""

echo "운영 관측 시작:"
bash scripts/evolution/l4_operational_drill.sh || {
    echo "⚠️  드릴 시작 실패 (수동 실행 권장)"
}
echo ""

# 5) 모니터링 가이드
echo "=== 5) 모니터링 가이드 ==="
echo ""

cat << 'EOF'
✅ 실행 완료! 이제 모니터링만 진행하면 됩니다.

📋 즉시 확인 (15분 SLO):
  bash scripts/evolution/quick_l4_check.sh

📋 정기 확인 (5~10분 주기, 30분간):
  # 5분마다 실행
  watch -n 300 bash scripts/evolution/quick_l4_check.sh

📋 24h 드릴 모니터링:
  # 실시간 로그
  sudo journalctl -u coldsync-install.service -f

  # 게이트 결정 추적
  watch -n 60 'grep -h "decision" var/evolution/EV-*/gate.json | tail -10'

  # 핵심 KPI 스냅샷
  jq -s '
    def m(a): (add/length) as $avg | {avg:$avg, min:min, max:max};
    {p_at3:(.[].p_at3)|m(.), stability:(.[].stability)|m(.),
     halluc_rate:(.[].halluc_rate)|m(.), rollback:(.[].rollback)|m(.)}
  ' var/evolution/EV-*/metrics.json 2>/dev/null

📋 24h 안착 기준:
  - PROMOTE ≥ 1, ROLLBACK = 0
  - stability ≥ 0.90, halluc_rate ≤ 0.08 (연속 2 윈도우)
  - 게이트 점수 G ≥ 0.70 (2회 연속)

📋 실패 시 즉시 조치:
  # 일시 차단
  bash scripts/bin/recover_coldsync.sh

  # 완전 롤백
  bash scripts/bin/rollback_coldsync.sh

📋 L4.1 선언 준비 (7일 목표):
  - 최근 48h G ≥ 0.75 지속
  - error_budget_burn(7d) ≤ 0.25, rollback_count(7d)=0
  - bash scripts/evolution/declare_l4.sh

EOF

echo ""
echo "=== 실행 완료 ==="
echo ""
echo "🎯 다음 단계: 모니터링만 진행하면 됩니다!"
echo ""
echo "📊 즉시 확인:"
echo "  bash scripts/evolution/quick_l4_check.sh"
echo ""
echo "📊 24h 드릴 모니터링:"
echo "  sudo journalctl -u coldsync-install.service -f"

