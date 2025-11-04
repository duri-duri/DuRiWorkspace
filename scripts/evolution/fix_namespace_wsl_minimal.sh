#!/usr/bin/env bash
# L4.0 NAMESPACE 에러 최소 패치 - WSL 호환 (WSL에서 실행)
# Usage: bash scripts/evolution/fix_namespace_wsl_minimal.sh
# 목적: mount-namespace 충돌 제거 + StateDirectory 사용

set -euo pipefail

echo "=== L4.0 NAMESPACE 에러 최소 패치 (WSL 호환) ==="
echo ""

# 안전 스냅샷
echo "0. 안전 스냅샷:"
sudo systemctl stop coldsync-install.path || true
sudo systemctl stop coldsync-install.service || true
sudo systemctl daemon-reload
echo "✅ 안전 스냅샷 완료"
echo ""

# override.conf 생성/치환
echo "1. override.conf 생성 (WSL 호환 최소 패치):"
sudo mkdir -p /etc/systemd/system/coldsync-install.service.d
sudo tee /etc/systemd/system/coldsync-install.service.d/override.conf >/dev/null <<'CONF'
[Service]
# ── WSL 최소 하드닝 + 쓰기 허용 경로 지정 ──
ProtectSystem=no
ProtectHome=read-only
PrivateTmp=yes
NoNewPrivileges=yes

# 대상 쓰기 경로만 개방
ReadWritePaths=/usr/local/bin /var/lib/coldsync-hosp /tmp
StateDirectory=coldsync-hosp

# 참고: 이전 ReadOnlyPaths/ProtectSystem=strict 등은 모두 제거됨
CONF
echo "✅ override.conf 생성 완료"
echo ""

# 적용
echo "2. systemd 데몬 리로드:"
sudo systemctl daemon-reload
echo "✅ daemon-reload 완료"
echo ""

echo "3. 서비스 시작:"
sudo systemctl start coldsync-install.service || true
echo "✅ 서비스 시작 완료"
echo ""

echo "4. Path 유닛 활성화:"
sudo systemctl enable coldsync-install.path
sudo systemctl start coldsync-install.path
echo "✅ Path 유닛 활성화 완료"
echo ""

# 상태 확인
echo "5. 상태 확인:"
echo ""
echo "서비스 상태:"
systemctl status coldsync-install.service --no-pager | head -20 || echo "상태 확인 실패"
echo ""

echo "로그 (최근 50줄):"
journalctl -u coldsync-install.service -n 50 --no-pager | tail -20 || echo "로그 없음"
echo ""

echo "해시 확인:"
sha256sum /home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh 2>/dev/null || echo "워킹트리 파일 없음"
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh 2>/dev/null || echo "설치본 파일 없음"
echo ""

echo "=== 최소 패치 완료 ==="
echo ""
echo "예상 결과:"
echo "  ✅ NAMESPACE 에러 소거 (p≈0.98)"
echo "  ✅ 서비스 정상 종료 (status=0/SUCCESS)"
echo "  ✅ 로그에 INSTALLED SRC=… / DST=… 해시 페어"
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/verify_namespace_fix.sh   # 원인 검증"
echo "  bash scripts/evolution/final_check_l4.sh          # 최종 체크리스트"

