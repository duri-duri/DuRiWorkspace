#!/usr/bin/env bash
set -euo pipefail

echo "🔍 systemd 유닛 정합성 검증 시작..."

echo "📋 1. 유닛 정합성 검증..."
if command -v systemd-analyze >/dev/null 2>&1; then
  for service in systemd/*.service; do
    echo "  📄 $(basename "$service")"
    systemd-analyze verify "$service" && echo "    ✅ PASS" || { echo "    ❌ FAIL"; exit 1; }
  done
else
  echo "  ⚠️  systemd-analyze 없음 - 건너뜀"
fi

echo "📋 2. systemd 유닛 설치..."
make install-systemd || true

echo "📋 3. 드롭인으로 짧은 주기 환경변수 주입..."
sudo mkdir -p /etc/systemd/system/duri-rag-eval.service.d
sudo tee /etc/systemd/system/duri-rag-eval.service.d/override.conf >/dev/null << 'OVR'
[Service]
Environment=SLEEP_SECS=10
OVR
sudo systemctl daemon-reload

echo "📋 4. 서비스 시작..."
sudo systemctl start duri-rag-eval

echo "📋 5. 상태 확인..."
sleep 2; systemctl --no-pager --full status duri-rag-eval | sed -n '1,40p'

echo "📋 6. 로그 확인..."
sudo journalctl -u duri-rag-eval -n 20 --no-pager

echo "📋 7. 산출물 확인..."
sleep 15
[[ -f .reports/train/day64/LATEST.tsv ]] && echo "  ✅ LATEST.tsv 생성됨" || echo "  ⚠️  LATEST.tsv 아직 생성되지 않음"

echo "📋 8. 스모크 완료 - 서비스 중지..."
sudo systemctl stop duri-rag-eval

echo "🎉 systemd 유닛 정합성 검증 & 스모크 완료!"
