#!/usr/bin/env bash
set -euo pipefail

# rotate_gates.sh (DURISSD에 최근 14개만 보존)
# DURISSD를 더 잘 쓰는 팁: 스테이징 디스크로만 쓰고, 로테이션 유지

SSD="/mnt/DURISSD/gates"
LOCAL_BASE="/home/duri/DuRiWorkspace"

echo "=== 🔄 게이트 로테이션 시작 ==="
echo "SSD 경로: ${SSD}"
echo "로컬 경로: ${LOCAL_BASE}"

# SSD 게이트 로테이션 (최근 14개만 보존)
if [ -d "$SSD" ]; then
    echo "📦 SSD 게이트 로테이션 (최근 14개만 보존)"
    cd "$SSD"
    count=$(ls -1 gate_*.tar.gz 2>/dev/null | wc -l)
    echo "   - 현재 게이트 수: $count"
    
    if [ $count -gt 14 ]; then
        to_remove=$((count - 14))
        echo "   - 삭제할 게이트 수: $to_remove"
        ls -1t gate_*.tar.gz | tail -n +15 | xargs -r rm -f
        echo "   ✅ SSD 로테이션 완료"
    else
        echo "   ✅ SSD 로테이션 불필요 (14개 이하)"
    fi
else
    echo "⚠️ SSD 경로 없음: $SSD"
fi

# 로컬 게이트 로테이션 (최근 7개만 보존)
echo "📦 로컬 게이트 로테이션 (최근 7개만 보존)"
cd "$LOCAL_BASE"
count=$(ls -1d gate_* 2>/dev/null | wc -l)
echo "   - 현재 로컬 게이트 수: $count"

if [ $count -gt 7 ]; then
    to_remove=$((count - 7))
    echo "   - 삭제할 로컬 게이트 수: $to_remove"
    ls -1td gate_* | tail -n +8 | xargs -r rm -rf
    echo "   ✅ 로컬 로테이션 완료"
else
    echo "   ✅ 로컬 로테이션 불필요 (7개 이하)"
fi

# 압축 파일 로테이션 (최근 5개만 보존)
count=$(ls -1 gate_*.tar.gz 2>/dev/null | wc -l)
echo "   - 현재 압축 파일 수: $count"

if [ $count -gt 5 ]; then
    to_remove=$((count - 5))
    echo "   - 삭제할 압축 파일 수: $to_remove"
    ls -1t gate_*.tar.gz | tail -n +6 | xargs -r rm -f
    echo "   ✅ 압축 파일 로테이션 완료"
else
    echo "   ✅ 압축 파일 로테이션 불필요 (5개 이하)"
fi

echo ""
echo "=== ✅ 게이트 로테이션 완료 ==="
echo "SSD 사용량: $(df -h $SSD 2>/dev/null | tail -1 | awk '{print $5}' || echo 'N/A')"
echo "로컬 사용량: $(du -sh . | cut -f1)"
echo ""
echo "🎯 권장 크론 설정:"
echo "   0 3 * * * $LOCAL_BASE/ops/rotate_gates.sh"
