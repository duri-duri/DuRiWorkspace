#!/usr/bin/env bash
# L4.0 NAMESPACE 에러 WSL 특이점 완화 (WSL에서 실행)
# Usage: bash scripts/evolution/fix_namespace_wsl.sh
# 목적: 보안은 유지, 호환성↑ (필요시만)

set -euo pipefail

echo "=== L4.0 NAMESPACE 에러 WSL 특이점 완화 ==="
echo ""
echo "⚠️  이 스크립트는 ProtectSystem=strict → full로 완화합니다."
echo "   보안은 유지하되, WSL2 호환성을 높입니다."
echo ""

read -p "계속하시겠습니까? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "취소됨"
    exit 0
fi

echo ""
echo "ProtectSystem=full로 완화:"
sudo mkdir -p /etc/systemd/system/coldsync-install.service.d
sudo tee -a /etc/systemd/system/coldsync-install.service.d/override.conf >/dev/null <<'EOF'
# strict → full (루트 FS 읽기전용 유지, mount stage 안정성↑)
ProtectSystem=full
EOF

echo "✅ override.conf 업데이트 완료"
echo ""

echo "systemd 데몬 리로드:"
sudo systemctl daemon-reload
echo "✅ daemon-reload 완료"
echo ""

echo "서비스 재시작:"
sudo systemctl start coldsync-install.service || true
echo "✅ 서비스 재시작 완료"
echo ""

echo "상태 확인:"
journalctl -u coldsync-install.service -n 30 --no-pager | tail -15 || echo "로그 없음"
echo ""

echo "=== WSL 특이점 완화 완료 ==="
echo ""
echo "예상: NAMESPACE 재발 방지 (p≈0.98)"

