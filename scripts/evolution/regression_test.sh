#!/usr/bin/env bash
# L4.0 회귀 테스트 (WSL에서 실행)
# Usage: bash scripts/evolution/regression_test.sh
# 목적: 자동 드리프트 복구 루프 검증

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 회귀 테스트 (자동 드리프트 복구 루프) ==="
echo ""

# 워크트리 소스는 duri 소유 + 실행권
echo "1. 파일 소유권/권한 정리:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
sudo chown duri:duri "$SRC_FILE"
chmod u+rwX "$SRC_FILE"
echo "✅ 소유권/권한 설정 완료"
echo ""

# 해시/유닛 스냅샷
echo "2. 해시/유닛 스냅샷:"
bash scripts/bin/status_coldsync_oneline.sh
echo ""

# 스모크: 소스에 단 한 줄 추가 → Path 유닛 트리거
echo "3. 스모크 테스트: 소스 수정 → Path 트리거:"
echo "# smoke: $(date)" >> "$SRC_FILE"
echo "✅ 소스 수정 완료"
echo ""

echo "4. Path 트리거 대기 (2초):"
sleep 2
echo ""

echo "5. 로그 확인 (INSTALLED/success/status=0):"
journalctl -u coldsync-install.service -n 50 --no-pager | grep -E 'INSTALLED|sha|success|status=0' || echo "로그 없음"
echo ""

echo "6. 해시 일치 확인:"
bash scripts/bin/status_coldsync_oneline.sh
echo ""

echo "7. 최종 프리플라이트:"
bash scripts/evolution/preflight_l4.sh
echo ""

echo "=== 회귀 테스트 완료 ==="
echo ""
echo "합격 기준:"
echo "  ✅ SRC==DST 해시 일치"
echo "  ✅ [INSTALLED] 성공 로그"
echo "  ✅ preflight_l4.sh GO/NO-GO == GO"
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/run_l4_timeline.sh   # 타임라인 실행"

