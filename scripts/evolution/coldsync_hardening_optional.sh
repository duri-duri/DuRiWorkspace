#!/usr/bin/env bash
# L4.0 coldsync 선택적 하드닝 (미세 조정)
# Usage: bash scripts/evolution/coldsync_hardening_optional.sh
# 목적: PATH 우선순위 고정, 디바운스 윈도 조정, Path 유닛 조건 강화 (선택)

set -euo pipefail

echo "=== L4.0 coldsync 선택적 하드닝 (미세 조정) ==="
echo ""

# 1) PATH 우선순위 고정
echo "1. PATH 우선순위 고정:"
if ! grep -q 'export PATH="$HOME/.local/bin' ~/.bashrc; then
    # .bashrc 맨 앞에 추가
    sed -i '1iexport PATH="$HOME/.local/bin:$PATH"' ~/.bashrc
    echo "✅ PATH 우선순위 추가 완료"
else
    echo "✅ PATH 우선순위 이미 설정됨"
fi
echo ""

# 2) 디바운스 윈도 확인/조정
echo "2. 디바운스 윈도 확인:"
WRAPPER="$HOME/.local/bin/coldsync_install_debounced.sh"
if [ -f "$WRAPPER" ]; then
    CURRENT_WIN=$(grep -E '^WIN=' "$WRAPPER" | head -1 | cut -d'=' -f2 | tr -d ' ')
    echo "현재 디바운스 윈도: ${CURRENT_WIN:-10}초"
    
    # 사용자에게 조정 여부 확인 (기본값 10초 유지)
    echo "디바운스 윈도 조정이 필요하면:"
    echo "  sed -i 's/WIN=10/WIN=15/' $WRAPPER"
    echo "  systemctl --user restart coldsync-install.path"
else
    echo "⚠️  디바운스 래퍼 없음: $WRAPPER"
fi
echo ""

# 3) Path 유닛 조건 강화 (소스 파일 존재 확인)
echo "3. Path 유닛 조건 강화:"
SRC_FILE="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
if [ -f "$SRC_FILE" ]; then
    echo "✅ 소스 파일 존재: $SRC_FILE"
    
    # Path 유닛에 ConditionPathExists 추가 (이미 있으면 무시)
    PATH_UNIT="$HOME/.config/systemd/user/coldsync-install.path"
    if [ -f "$PATH_UNIT" ]; then
        if ! grep -q 'ConditionPathExists=' "$PATH_UNIT"; then
            # [Unit] 섹션에 추가
            sed -i '/^\[Unit\]/a ConditionPathExists=%h/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh' "$PATH_UNIT"
            echo "✅ Path 유닛 조건 강화 완료"
            systemctl --user daemon-reload
            systemctl --user restart coldsync-install.path
        else
            echo "✅ Path 유닛 조건 이미 설정됨"
        fi
    fi
else
    echo "⚠️  소스 파일 없음: $SRC_FILE"
fi
echo ""

# 4) .bashrc 적용 및 확인
echo "4. .bashrc 적용 및 확인:"
source ~/.bashrc || true
if command -v cold_status >/dev/null 2>&1; then
    echo "✅ cold_status 명령어 사용 가능"
else
    echo "⚠️  cold_status 명령어 미인식 (경고 무시 가능)"
fi
echo ""

echo "=== 선택적 하드닝 완료 ==="
echo ""
echo "다음 단계:"
echo "  cold-status"
echo "  cold-hash"

