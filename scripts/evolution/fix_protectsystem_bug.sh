#!/usr/bin/env bash
# L4.0 NAMESPACE 에러 핫픽스 - ProtectSystem 버그 수정 (WSL에서 실행)
# Usage: bash scripts/evolution/fix_protectsystem_bug.sh
# 목적: ProtectSystem=no 명시 + ReadWritePaths 지정

set -euo pipefail

echo "=== L4.0 ProtectSystem 버그 핫픽스 ==="
echo ""

# 1) drop-in 재작성
echo "1. override.conf 재작성:"
sudo install -d -m 0755 /etc/systemd/system/coldsync-install.service.d
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

# 참고: 이전 ReadOnlyPaths/ProtectSystem=strict 등은 모두 제거됨
CONF
echo "✅ override.conf 재작성 완료"
echo ""

# 2) 재로드 & 유닛 재시작
echo "2. systemd 데몬 리로드:"
sudo systemctl daemon-reload
echo "✅ daemon-reload 완료"
echo ""

echo "3. Path 유닛 재시작:"
sudo systemctl restart coldsync-install.path
echo "✅ Path 유닛 재시작 완료"
echo ""

echo "4. 서비스 수동 1회 실행:"
sudo systemctl start coldsync-install.service
echo "✅ 서비스 시작 완료"
echo ""

# 3) 상태/로그 확인
echo "5. 상태/로그 확인:"
echo ""
echo "서비스 상태:"
systemctl status --no-pager coldsync-install.service || true
echo ""

echo "로그 (최근 50줄):"
journalctl -u coldsync-install.service -n 50 --no-pager | tail -20 || echo "로그 없음"
echo ""

# ProtectSystem 파싱 에러 확인
echo "6. ProtectSystem 파싱 에러 확인:"
PARSE_ERRORS=$(journalctl -u coldsync-install.service -n 200 --no-pager | grep -cE 'Failed to parse protect system value' || echo "0")
if [ "$PARSE_ERRORS" -eq 0 ]; then
    echo "✅ ProtectSystem 파싱 에러 없음"
else
    echo "⚠️  ProtectSystem 파싱 에러 발견 ($PARSE_ERRORS건)"
fi
echo ""

# 서비스 결과 확인
echo "7. 서비스 결과 확인:"
SERVICE_RESULT=$(systemctl show coldsync-install.service -p Result --value 2>/dev/null || echo "unknown")
if [ "$SERVICE_RESULT" = "success" ]; then
    echo "✅ 서비스 성공 (Result=success)"
else
    echo "⚠️  서비스 결과: $SERVICE_RESULT"
fi
echo ""

echo "=== 핫픽스 완료 ==="
echo ""
echo "기대 로그:"
echo "  ✅ 'Failed to parse protect system value' 경고 사라짐"
echo "  ✅ installed/up-to-date 메시지"
echo "  ✅ status=0/SUCCESS"
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/verify_protectsystem_fix.sh   # 검증"
echo "  bash scripts/evolution/fix_installer_exit.sh          # 설치기 exit 0 보장"

