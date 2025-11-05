#!/usr/bin/env bash
# L4.0 ExecStartPre 제거 및 소스 파일 확인 (WSL에서 실행)
# Usage: bash scripts/evolution/fix_execstartpre.sh
# 목적: ExecStartPre 제거 및 소스 파일 확인

set -euo pipefail

echo "=== L4.0 ExecStartPre 제거 및 소스 파일 확인 ==="
echo ""

# 1. 소스 파일 확인
echo "1. 소스 파일 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
if [ -f "$SRC_FILE" ]; then
    echo "✅ 소스 파일 존재: $SRC_FILE"
    ls -la "$SRC_FILE"
    
    if [ -r "$SRC_FILE" ]; then
        echo "✅ 읽기 가능"
    else
        echo "❌ 읽기 불가 → 권한 수정"
        sudo chmod 0644 "$SRC_FILE" || true
        sudo chown duri:duri "$SRC_FILE" || true
    fi
else
    echo "❌ 소스 파일 없음: $SRC_FILE"
    echo "📋 파일 생성 필요"
fi
echo ""

# 2. override.conf 업데이트 (ExecStartPre 명시적 제거)
echo "2. override.conf 업데이트 (ExecStartPre 명시적 제거):"
sudo mkdir -p /etc/systemd/system/coldsync-install.service.d
sudo tee /etc/systemd/system/coldsync-install.service.d/override.conf >/dev/null <<'CONF'
[Service]
# ── WSL 최소 하드닝 + 쓰기 허용 경로 지정 ──
ProtectSystem=no
ProtectHome=no
PrivateTmp=yes
NoNewPrivileges=yes

# 대상 쓰기 경로만 개방
ReadWritePaths=/usr/local/bin /var/lib/coldsync-hosp /tmp
# 소스 파일 읽기 허용 (ProtectHome=no로도 가능하지만 명시적)
ReadOnlyPaths=/home/duri/DuRiWorkspace/scripts/bin
StateDirectory=coldsync-hosp

# ExecStartPre 명시적 제거 (본 서비스 파일의 ExecStartPre 무시)
ExecStartPre=
CONF
echo "✅ override.conf 업데이트 완료"
echo ""

# 3. 데몬 리로드
echo "3. systemd 데몬 리로드:"
sudo systemctl daemon-reload
echo "✅ daemon-reload 완료"
echo ""

# 4. 서비스 시작 테스트
echo "4. 서비스 시작 테스트:"
sudo systemctl start coldsync-install.service || true
echo ""

# 5. 상태 확인
echo "5. 상태 확인:"
systemctl status coldsync-install.service --no-pager | head -20 || echo "상태 확인 실패"
echo ""

echo "로그 (최근 20줄):"
journalctl -u coldsync-install.service -n 20 --no-pager | tail -10 || echo "로그 없음"
echo ""

echo "=== ExecStartPre 제거 완료 ==="
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/verify_protectsystem_fix.sh   # 검증"

