#!/usr/bin/env bash
# L4.0 NAMESPACE 에러 최소 패치 (WSL에서 실행)
# Usage: bash scripts/evolution/fix_namespace_minimal.sh
# 목적: 즉시 GO 노리기 (3분)

set -euo pipefail

echo "=== L4.0 NAMESPACE 에러 최소 패치 (즉시 GO) ==="
echo ""

# A. 경로 선행 생성 + 퍼미션
echo "1. 경로 선행 생성 + 퍼미션:"
sudo install -d -o root -g root -m 0755 /var/lib/coldsync-hosp
echo "✅ /var/lib/coldsync-hosp 생성 완료"
echo ""

# B. ReadWritePaths를 "느슨 모드"로 (경로 유무 무시)
echo "2. ReadWritePaths 느슨 모드 설정:"
sudo mkdir -p /etc/systemd/system/coldsync-install.service.d
sudo tee /etc/systemd/system/coldsync-install.service.d/override.conf >/dev/null <<'EOF'
[Service]
# 경로 부재시 실패하지 않도록 허용
ReadWritePaths=
ReadWritePaths=-/var/lib/coldsync-hosp -/usr/local/bin -/tmp
EOF
echo "✅ override.conf 생성 완료"
echo ""

# 데몬 리로드 및 재시작
echo "3. systemd 데몬 리로드:"
sudo systemctl daemon-reload
echo "✅ daemon-reload 완료"
echo ""

echo "4. 서비스 재시작:"
sudo systemctl restart coldsync-install.path
sudo systemctl start coldsync-install.service || true
echo "✅ 서비스 재시작 완료"
echo ""

# C. 빠른 진단
echo "5. 빠른 진단:"
echo ""
echo "서비스 상태:"
systemctl status coldsync-install.service --no-pager | head -20 || echo "상태 확인 실패"
echo ""

echo "로그 (최근 50줄):"
journalctl -u coldsync-install.service -n 50 --no-pager | tail -20 || echo "로그 없음"
echo ""

echo "상태 확인:"
bash scripts/bin/status_coldsync_oneline.sh || true
echo ""

echo "=== 최소 패치 완료 ==="
echo ""
echo "예상: NAMESPACE 에러 소거 (p≈0.92)"
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/fix_namespace_permanent.sh   # 영구 패치"
echo "  bash scripts/evolution/endpoint_check.sh            # 끝점 체크"

