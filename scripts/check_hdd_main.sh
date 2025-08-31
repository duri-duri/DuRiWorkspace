#!/usr/bin/env bash
set -Eeuo pipefail
TS(){ date "+%F %T"; }; log(){ echo "[$(TS)] $*"; }

echo "=== HDD 메인 전환 완료 여부 확인 (4가지 AND 판정) ==="

# (1) HDD/FULL 산출물 존재
echo "1) HDD/FULL 산출물 확인:"
HDD_FULL="$(find /mnt/hdd/ARCHIVE/FULL -type f -name 'FULL__*.tar.zst' 2>/dev/null | head -1)"
if [[ -n "$HDD_FULL" ]]; then
    echo "✅ HDD FULL 백업 존재: $HDD_FULL"
    HDD_EXISTS=true
else
    echo "❌ HDD FULL 백업 없음"
    HDD_EXISTS=false
fi

# (2) 백업 실행 후 로그에 PRIMARY=/mnt/hdd/ARCHIVE/FULL/... 기록
echo -e "\n2) PRIMARY 로그 확인:"
PRIMARY_LOG="$(grep -R "PRIMARY=/mnt/hdd/ARCHIVE/FULL" /var/log/duri2-backup 2>/dev/null | tail -1)"
if [[ -n "$PRIMARY_LOG" ]]; then
    echo "✅ PRIMARY 로그 발견: $PRIMARY_LOG"
    PRIMARY_LOGGED=true
else
    echo "❌ PRIMARY 로그 없음"
    PRIMARY_LOGGED=false
fi

# (3) 스탬프 파일 갱신
echo -e "\n3) 스탬프 파일 확인:"
STAMP_FILE="/mnt/hdd/ARCHIVE/FULL/.last_full_backup.txt"
TOPOLOGY_FILE="/mnt/hdd/ARCHIVE/FULL/.topology.json"
if [[ -f "$STAMP_FILE" && -f "$TOPOLOGY_FILE" ]]; then
    echo "✅ 스탬프 파일 존재:"
    echo "   - $STAMP_FILE: $(ls -l "$STAMP_FILE")"
    echo "   - $TOPOLOGY_FILE: $(ls -l "$TOPOLOGY_FILE")"
    STAMPS_EXIST=true
else
    echo "❌ 스탬프 파일 없음"
    STAMPS_EXIST=false
fi

# (4) DR 검사 통과
echo -e "\n4) DR 검사:"
if ./scripts/disaster_recovery.sh >/dev/null 2>&1; then
    echo "✅ DR 검사 통과"
    DR_OK=true
else
    echo "❌ DR 검사 실패"
    DR_OK=false
fi

# 종합 판정
echo -e "\n=== 종합 판정 ==="
if [[ "$HDD_EXISTS" == "true" && "$PRIMARY_LOGGED" == "true" && "$STAMPS_EXIST" == "true" && "$DR_OK" == "true" ]]; then
    echo "🎉 HDD 메인 전환 완료! (확률≥0.99)"
    exit 0
else
    echo "⚠️ HDD 메인 전환 미완료"
    echo "   - HDD 산출물: $HDD_EXISTS"
    echo "   - PRIMARY 로그: $PRIMARY_LOGGED"
    echo "   - 스탬프 파일: $STAMPS_EXIST"
    echo "   - DR 검사: $DR_OK"
    exit 1
fi
