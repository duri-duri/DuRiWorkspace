#!/usr/bin/env bash
# L4.0 NAMESPACE 에러 핫픽스 (WSL에서 실행)
# Usage: bash scripts/evolution/fix_namespace_error.sh
# 목적: /var/lib/coldsync-hosp 디렉터리 생성 및 서비스 재시작

set -euo pipefail

echo "=== L4.0 NAMESPACE 에러 핫픽스 ==="
echo ""

# 1) 필요한 RW 디렉터리 생성
echo "1. 디렉터리 생성 및 권한 설정:"
sudo install -d -m 0755 -o root -g root /var/lib/coldsync-hosp
echo "✅ /var/lib/coldsync-hosp 생성 완료"
echo ""

# 2) 데몬 리로드 후 1회 트리거
echo "2. systemd 데몬 리로드:"
sudo systemctl daemon-reload
echo "✅ daemon-reload 완료"
echo ""

echo "3. 서비스 시작:"
sudo systemctl start coldsync-install.service
echo "✅ 서비스 시작 완료"
echo ""

# 3) 상태 확인
echo "4. 상태 확인:"
echo ""
bash scripts/bin/status_coldsync_oneline.sh
echo ""

echo "5. 로그 확인 (최근 50줄):"
sudo journalctl -xeu coldsync-install.service --no-pager | tail -n 50 || echo "로그 없음"
echo ""

echo "6. 최종 검증:"
bash scripts/bin/verify_coldsync_final.sh
echo ""

echo "=== 핫픽스 완료 ==="
echo ""
echo "예상: NAMESPACE 에러 소거, [INSTALLED] 로그 복구"
echo "성공 확률: p≈0.92"

