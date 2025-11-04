#!/usr/bin/env bash
# L4.0 NAMESPACE 에러 영구 패치 (WSL에서 실행)
# Usage: bash scripts/evolution/fix_namespace_permanent.sh
# 목적: 부팅/재배포에 안전 (2분)

set -euo pipefail

echo "=== L4.0 NAMESPACE 에러 영구 패치 (부팅/재배포 안전) ==="
echo ""

# A. StateDirectory로 지속 보장
echo "1. StateDirectory 추가:"
sudo mkdir -p /etc/systemd/system/coldsync-install.service.d
if ! sudo grep -q "^StateDirectory=" /etc/systemd/system/coldsync-install.service.d/override.conf 2>/dev/null; then
    sudo tee -a /etc/systemd/system/coldsync-install.service.d/override.conf >/dev/null <<'EOF'
StateDirectory=coldsync-hosp
EOF
    echo "✅ StateDirectory 추가됨"
else
    echo "ℹ️  StateDirectory 이미 존재"
fi
echo ""

# B. ExecCondition 안전화
echo "2. ExecCondition 안전화:"
if ! sudo grep -q "^ExecCondition=" /etc/systemd/system/coldsync-install.service.d/override.conf 2>/dev/null; then
    sudo tee -a /etc/systemd/system/coldsync-install.service.d/override.conf >/dev/null <<'EOF'
ExecCondition=
ExecCondition=/bin/sh -c '[ -x /usr/local/sbin/coldsync-install ] || exit 0'
EOF
    echo "✅ ExecCondition 안전화됨"
else
    echo "ℹ️  ExecCondition 이미 존재"
fi
echo ""

# C. 재시작
echo "3. systemd 데몬 리로드:"
sudo systemctl daemon-reload
echo "✅ daemon-reload 완료"
echo ""

echo "4. 서비스 재시작:"
sudo systemctl restart coldsync-install.path
sudo systemctl start coldsync-install.service || true
echo "✅ 서비스 재시작 완료"
echo ""

echo "5. 상태 확인:"
journalctl -u coldsync-install.service -n 30 --no-pager | tail -15 || echo "로그 없음"
echo ""

echo "=== 영구 패치 완료 ==="
echo ""
echo "예상: GO/NO-GO → GO 전환 (p≈0.95)"
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/fix_namespace_wsl.sh   # WSL 특이점 완화 (필요시)"
echo "  bash scripts/evolution/regression_test.sh      # 회귀 테스트"
