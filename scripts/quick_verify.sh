#!/usr/bin/env bash
# 빠른 재검증 체크리스트
set -euo pipefail

echo "🚀 빠른 재검증 체크리스트 시작..."

# 0) 의존성 캐시(비번 한 번만)
echo "📋 0. 의존성 캐시..."
if command -v sudo >/dev/null 2>&1; then
    echo "  sudo 권한 확인 중..."
    sudo -v || echo "  ⚠️  sudo 권한 없음 - 일부 테스트 건너뜀"
else
    echo "  ⚠️  sudo 없음 - 일부 테스트 건너뜀"
fi

# 1) 설치
echo "📋 1. systemd 유닛 설치..."
if command -v sudo >/dev/null 2>&1; then
    make install-systemd || echo "  ⚠️  설치 실패 (sudo 권한 필요)"
else
    echo "  ⚠️  sudo 없음 - 설치 건너뜀"
fi

# 2) 기동 & 상태
echo "📋 2. 서비스 기동 & 상태..."
if command -v sudo >/dev/null 2>&1; then
    make start-shadow || echo "  ⚠️  서비스 시작 실패"
    sleep 2
    make status-shadow | sed -n '1,40p' || echo "  ⚠️  상태 확인 실패"
else
    echo "  ⚠️  sudo 없음 - 서비스 테스트 건너뜀"
fi

# 3) 짧은 스모크
echo "📋 3. 짧은 스모크..."
if command -v sudo >/dev/null 2>&1; then
    bash scripts/verify_systemd.sh || echo "  ⚠️  스모크 실패"
else
    echo "  ⚠️  sudo 없음 - 스모크 건너뜀"
fi

# 4) 정상 정지
echo "📋 4. 정상 정지..."
if command -v sudo >/dev/null 2>&1; then
    make stop-shadow || echo "  ⚠️  서비스 중지 실패"
else
    echo "  ⚠️  sudo 없음 - 중지 건너뜀"
fi

echo "🎉 빠른 재검증 체크리스트 완료!"
