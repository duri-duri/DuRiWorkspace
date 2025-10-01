#!/usr/bin/env bash
set -Eeuo pipefail
TS() { date '+%F %T'; }
log(){ echo "[$(TS)] $*"; }

# === DuRi 콜드 백업 수동 동기화 스크립트 ===
# 목적: 드라이브 교체 시 수동으로 동기화 실행
# 사용법: ./scripts/manual_cold_backup_sync.sh

echo "🔄 DuRi 콜드 백업 수동 동기화"
echo "================================"
echo ""
echo "이 스크립트는 다음 상황에서 사용합니다:"
echo "1. 병원용 드라이브를 집으로 가져온 경우"
echo "2. 집용 드라이브를 병원으로 가져온 경우"
echo "3. 두 드라이브가 모두 연결된 경우"
echo ""

# 현재 연결된 드라이브 확인
echo "📋 현재 연결된 드라이브 확인:"
echo ""

HOSP_CONNECTED=false
HOME_CONNECTED=false

if mountpoint -q "/mnt/e" 2>/dev/null; then
    echo "✅ 병원용 콜드 백업 드라이브 연결됨: /mnt/e"
    HOSP_CONNECTED=true
else
    echo "❌ 병원용 콜드 백업 드라이브 연결 안됨: /mnt/e"
fi

if mountpoint -q "/mnt/f" 2>/dev/null; then
    echo "✅ 집용 콜드 백업 드라이브 연결됨: /mnt/f"
    HOME_CONNECTED=true
else
    echo "❌ 집용 콜드 백업 드라이브 연결 안됨: /mnt/f"
fi

echo ""

# 동기화 방향 결정
if [[ "$HOSP_CONNECTED" == true && "$HOME_CONNECTED" == true ]]; then
    echo "🔄 양방향 동기화 가능"
    echo "1. 병원용 → 집용 동기화"
    echo "2. 집용 → 병원용 동기화"
    echo "3. 양방향 동기화 (최신 파일 기준)"
    echo ""
    read -p "선택하세요 (1/2/3): " choice

    case $choice in
        1)
            echo "📁 병원용 → 집용 동기화 실행..."
            ./scripts/duri_cold_backup_home.sh
            ;;
        2)
            echo "📁 집용 → 병원용 동기화 실행..."
            # 집용에서 병원용으로 동기화하는 스크립트 실행
            COLD_HOME="/mnt/f/DuRiSafe_HOME"
            COLD_HOSP="/mnt/e/DuRiSafe_HOSP"

            # 최신 백업 파일 찾기
            LATEST_HOME=$(find "$COLD_HOME/FULL" -name "FULL__*.tar.zst" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
            if [[ -n "$LATEST_HOME" ]]; then
                BASENAME_HOME=$(basename "$LATEST_HOME")
                LATEST_HOSP="$COLD_HOSP/FULL/$BASENAME_HOME"

                echo "집용 최신 백업: $BASENAME_HOME"

                if [[ ! -f "$LATEST_HOSP" ]]; then
                    echo "📁 백업 파일 복사 중..."
                    cp "$LATEST_HOME" "$LATEST_HOSP"
                    echo "✅ 복사 완료"
                else
                    echo "✅ 병원용에 이미 동일한 파일 존재"
                fi
            else
                echo "❌ 집용에 백업 파일이 없습니다"
            fi
            ;;
        3)
            echo "📁 양방향 동기화 실행..."
            ./scripts/duri_cold_backup_home.sh
            # 집용에서 병원용으로도 동기화
            COLD_HOME="/mnt/f/DuRiSafe_HOME"
            COLD_HOSP="/mnt/e/DuRiSafe_HOSP"
            LATEST_HOME=$(find "$COLD_HOME/FULL" -name "FULL__*.tar.zst" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
            if [[ -n "$LATEST_HOME" ]]; then
                BASENAME_HOME=$(basename "$LATEST_HOME")
                LATEST_HOSP="$COLD_HOSP/FULL/$BASENAME_HOME"
                if [[ ! -f "$LATEST_HOSP" ]]; then
                    cp "$LATEST_HOME" "$LATEST_HOSP"
                    echo "✅ 집용 → 병원용 복사 완료"
                fi
            fi
            ;;
        *)
            echo "❌ 잘못된 선택입니다"
            exit 1
            ;;
    esac

elif [[ "$HOSP_CONNECTED" == true ]]; then
    echo "📁 병원용 드라이브만 연결됨"
    echo "집용 드라이브를 연결한 후 다시 실행하세요"

elif [[ "$HOME_CONNECTED" == true ]]; then
    echo "📁 집용 드라이브만 연결됨"
    echo "병원용 드라이브를 연결한 후 다시 실행하세요"

else
    echo "❌ 콜드 백업 드라이브가 연결되지 않았습니다"
    echo "드라이브를 연결한 후 다시 실행하세요"
fi

echo ""
echo "✅ 동기화 작업 완료"
